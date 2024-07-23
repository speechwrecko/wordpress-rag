#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""

import os
from flask import Flask, render_template, request, url_for, jsonify, flash, redirect
from dotenv import load_dotenv

from scraper import scraper
from db import db, embeddings
from chat import chat

DEVELOPMENT_ENV = False

app = Flask(__name__)

app_data = {
    "name": "Wordpress RAG",
    "description": "Get answers to questions from any Wordpress blog",
    "author": "Jason Flaks",
    "html_title": "Wordpress RAG",
    "project_name": "Wordpress RAG",
    "keywords": "wordpress, rag, llm",
    "answer": "",
}

@app.route("/")
def index():
    return render_template("index.html", app_data=app_data)


@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)


@app.route("/contact")
def service():
    return render_template("contact.html", app_data=app_data)


@app.route("/process_query", methods=('GET', 'POST'))
def process_query():
    result = 500
    if request.method == 'POST':
        query = request.form['queryInput']
        if not query:
            flash('You must ask a question!')
            result = 500
        else:
            app_data["answer"] = get_answer(query)
            result = 204
            #return redirect(url_for('index'))
            
    #return '', 204
    #return render_template("index.html", app_data=app_data)
    return redirect(url_for('index'))

def get_answer(query):
    try:
        res = vectordb.search(query)
        chatbot = chat("anthropic")
        message = chatbot.create_response(query, data_path + "/" + res)
    except:
        message = "Sorry I am broken!!!"
    return message


def main():
    global data_path
    global vectordb

    load_dotenv()
    blog_url = os.getenv('BLOG_POST_URL')
    data_path = "blog_files"
    vectordb = db("wordpress_rag.db", "wordpress_collection", 768, "default", False)

    if not vectordb.is_data_loaded():
        blog_scraper = scraper(blog_url)
        post_urls = blog_scraper.get_wordpress_posts()
        blog_scraper.extract_text_from_posts(post_urls)

        vectordb = db("wordpress_rag.db", "wordpress_collection", 768, "default", False)
        vectordb.load_data(data_path)

    app.run(debug=DEVELOPMENT_ENV)


if __name__ == "__main__":
    main()
    