from pymilvus import MilvusClient
from pymilvus import model
from sentence_transformers import SentenceTransformer
import os
import re
import json
import time
from scraper import logger

class db:
    def __init__(self, db_name, collection_name, vector_dimension, embedding_type, drop_existing):
        self.client =  MilvusClient(db_name)
        self.collection_name = collection_name
        self.dimension = vector_dimension
        self.embedding_model = embeddings(embedding_type)
        self.data_loaded = False

        if self.client.has_collection(collection_name=self.collection_name):
            if drop_existing:
                self.client.drop_collection(collection_name=self.collection_name)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    dimension=vector_dimension,  # The vectors we will use in this demo has 768 dimensions
                )
            else:
                self.data_loaded = True
        else:
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=vector_dimension,  # The vectors we will use in this demo has 768 dimensions
            )

    def is_data_loaded(self):
        return self.data_loaded

    def load_data(self, data_path):
        #data = []
        log_object = logger()
        id = 0

        for file in os.listdir(data_path):
            filename = os.fsdecode(file)
            if filename.endswith(".txt"):
                file_data = []
                f = open(data_path + "/" + file, "r")
                sent_array = re.split(r"[.!?](?!$)", f.read())
                sent_array = [s.strip() for s in sent_array if s != ' ' and s != '"' and s != '']
                vectors = self.embedding_model.generate_embeddings(sent_array)
                file_data = [
                    {"id": id, "vector": vectors[i], "text": sent_array[i], "title": filename} 
                    for i in range(len(vectors))
                ]
                id += 1
                self.client.upsert(collection_name=self.collection_name, data=file_data)
                log_object.update_scrape_event(filename.replace(".txt", ""), {"db_is_inserted": True, "db_inserted_timestamp": time.time()})

    def search(self, query_string):
        query_vectors = self.embedding_model.generate_query_embeddings(query_string)
        
        search_params = {
            "metric_type": "COSINE",
            "params": {
                "radius": 0.1,
                "range_filter": 1.0
            }
        }

        res = self.client.search(
            collection_name=self.collection_name,  # target collection
            data=query_vectors,  # query vectors
            limit=3,  # number of returned entities
            search_params = search_params,
            output_fields=["text", "title"],  # specifies fields to be returned
        )
        result = json.dumps(res, indent=4)
        print(result)
        titles = []
        if len(res[0]) > 0:
            titles = [r["entity"]["title"] for r in list(res[0])]
            titles = list(dict.fromkeys(titles))

        return titles

class embeddings:
    def __init__(self, type):
        self.type = type
        if type == "default":
            # This will download a small embedding model "paraphrase-albert-small-v2" (~50MB).
           self.embedding_fn = model.DefaultEmbeddingFunction()
        elif type == "bert":
            self.embedding_fn = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        else:
            raise ValueError
        
    def generate_embeddings(self, sentence_array):
        vectors = None
        if self.type == "default":
            vectors = self.embedding_fn.encode_documents(sentence_array)
        elif self.type == "bert":
            vectors = self.embedding_fn.encode(sentence_array)
        return vectors
    
    def generate_query_embeddings(self, query_string):
        vectors = None
        if self.type == "default":
            vectors = self.embedding_fn.encode_queries([query_string])
        elif self.type == "bert":
            vectors = self.embedding_fn.encode([query_string])
        return vectors




    
