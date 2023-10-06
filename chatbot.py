# Chatbot using OpenAI's GPT-3 API
import pandas as pd
import numpy as np
import openai
import os
import redis
from redis.commands.search.query import Query


REDIS_HOST =  "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = "" # default for passwordless Redis

class Chatbot:

    def __init__(self):

        openai.api_key = os.environ.get('OPENAI_KEY')
        self.init_history = [
            {"role": "system", "content": "You are a helpful assistant. Answer questions, summarize information and list up key findins in the text provided in the chat. Let's think step by step. Answer in the language of the user."},
            {"role": "user", "content": "Jeg er en kvinne på 82år og lurer på vaksiner.\n\nText: 'Bør tas innen 1. mai - I Stavanger kommune kan oppfriskningsdosen fås i vaksinesenteret i Hjalmar Johansens gate 10. Noen fastleger setter også oppfriskningsdose, så sjekk med fastlegen. Sykehjemsbeboere får tilbud om oppfriskningsdose der de bor.'"},
            {"role": "assistant", "content": "Nå kan du få oppfriskingsdose, helst før 1.mai. Vaksinen får du på vaksinesenteret i Hjalmar Johansens gate 10. Sykehjem og noen fastleger kan også sette vaksinen" }
        ] 
        self.history = self.init_history
        self.output_history = ['']
        try:
            self.redis_client = redis.Redis(
                                    host=REDIS_HOST,
                                    port=REDIS_PORT,
                                    password=REDIS_PASSWORD
                                )
            print("Redis connection established")
        except Exception as e:
            print("Redis connection failed")
            print(e)
        self.context_history = []
        self.msg_history = ''

    def reset_history(self):
        self.history = self.init_history
        self.output_history = ['']


    def search_redis(self,
        user_query: str,
        index_name: str = "embeddings-index",
        vector_field: str = "content_vector",
        return_fields: list = ["title", "url", "text", "vector_score"],
        hybrid_fields = "*",
        k: int = 20,
        print_results: bool = False,
    ) -> list[dict]:

        # Creates embedding vector from user query
        embedded_query = openai.Embedding.create(input=user_query,
                                                model="text-embedding-ada-002",
                                                )["data"][0]['embedding']

        # Prepare the Query
        base_query = f'{hybrid_fields}=>[KNN {k} @{vector_field} $vector AS vector_score]'
        query = (
            Query(base_query)
            .return_fields(*return_fields)
            .sort_by("vector_score")
            .paging(0, k)
            .dialect(2)
        )
        params_dict = {"vector": np.array(embedded_query).astype(dtype=np.float32).tobytes()}

        # perform vector search
        results = self.redis_client.ft(index_name).search(query, params_dict)
        if print_results:
            for i, article in enumerate(results.docs):
                score = 1 - float(article.vector_score)
                print(f"{i}. {article.title} (Score: {round(score ,3) })")
        return results.docs
    
    # define the chatbot logic
    def chatbot_response(self, msg):
        self.msg_history += ' ' + msg
        context = self.search_redis(self.msg_history)
        # check if the context has been served before:
        context_url = ''
        for c in context:
            if c.id not in self.context_history:
                # combine the user input with the bot's previous response
                context_text = c.text.replace('\n', '').replace('\xa0','') 
                context_url = c.url
                print('ChatGPT prompt --------- \n' + msg + "\n\nText:'" +  context_text + "'")
                self.history.append({"role": "user", "content": msg + "\n\nText:'" +  context_text + "'"})
                self.context_history.append(c.id)
                break

        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=self.history
        )
        # append the bot's response to the chat history
        self.history.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
        # update the output history - what is displayed in the chat window
        self.output_history.append("Human: " + msg)
        if context_url:
            url = context_url.replace('index.html', '')
            #self.output_history.append("Bot: " + response['choices'][0]['message']['content'] + "\n <a href=" + url + '" >' + url +'</a>')
            self.output_history.append("Bot: " + response['choices'][0]['message']['content'] + "\n" + url)

        else:
            self.output_history.append("Bot: " + response['choices'][0]['message']['content'])

        return response['choices'][0]['message']['content']