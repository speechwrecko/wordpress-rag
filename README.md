# Basic RAG implementation for Wordpress blogs

A basic implementation of RAG for any worpress blog. Leverages the Milvus vector DB.  Options for either using OpenAI or Anthropic as your LLM and Sentence BERT for embeddings.

On first run all blog posts will be scrapped. Embeddings are based on sentence parsing of each post.

![alt text](https://github.com/speechwrecko/wordpress-rag/blob/master/wordpress_rag_screenshot.png?raw=true)

## Running Locally

Make sure you have Python installed

```sh
$ git clone https://github.com/speechwrecko/wordpress-rag.git # or clone your own fork
$ cd wordpress-rag
$ pip install -r requirements.txt
$ python app.py
```

Your app should now be running on [localhost:5000](http://localhost:5000/).

## Credits
### Initial basis for flask / bootstrap implementation

Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023