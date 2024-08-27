#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, request, url_for, jsonify, flash, redirect
from dotenv import load_dotenv
import logging

from scraper import scraper, logger
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
    "source": "",
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
            app_data["answer"], app_data["source"] = get_answer(query)
            result = 204

    return redirect(url_for('index'))

def get_answer(query):
    try:
        source = vectordb.search(query)
        print(source)
        chatbot = chat("anthropic")
        message = chatbot.create_response(query, data_path, source)
    except Exception as e:
        print(e)
        message = "Sorry I am broken!!!"

    return message, (", ".join(source)).replace(".txt", "")


def main():
    global data_path
    global vectordb

    load_dotenv()
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    blog_url = os.getenv('BLOG_POST_URL')
    diffbot_token = os.getenv('DIFFBOT_TOKEN')
    data_path = "blog_files"

    blog_scraper = scraper(blog_url, diffbot_token)
    log_object = logger()

    logging.info("getting wordpress post URLs")    
    post_urls = blog_scraper.get_wordpress_posts()

    logging.info("Extracting text if not already extracted")
    blog_scraper.extract_text_from_posts(post_urls)

    logging.info("creating DB and collection")
    vectordb = db("wordpress_rag.db", "wordpress_collection", 768, "default", False)
    
    if vectordb.is_data_loaded() == False or log_object.is_all_inserted() == False:
        logging.info("upserting any new info")
        vectordb.load_data(data_path)
    logging.info("starting FLASK server")

    app.run(debug=DEVELOPMENT_ENV)


if __name__ == "__main__":
    main()
    