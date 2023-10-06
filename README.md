# Scrape Stavanger Kommune's open data portal
## https://stavanger.kommune.no/

1. get the html files


    ```bash
    wget -P / --recursive https://www.stavanger.kommune.no/      
    ````

2. convert to text
    
    ```bash
    for file in $(find . -type f -name "*.html"); do html2text "$file" > "$file.txt"; done 
    ```

3. start a redis server using docker compose

    ```bash
    docker-compose up -d
    ```

4. pars and embedd text using OpenAi in **parse_website.ipynb**

5. store data in redis and create vector index using **redis.ipynb**


## How it works, same as ChatGPT Plugins
[Title](https://github.com/openai/openai-cookbook)

ChatGPT plugins was announced on last week, and by coincident I finished a customised chatbot MVP the same week based on the same consepts. This is how they work.

New Bing search also uses the same concepts. What you need is the ChatGPT API, a custom data source and a way to query the data source effectively based on the user input.

Step by step:

1. Get access to the ChatGPT API

2. Create a custom data source. This can be a internal database, web page, API or files.

3. Create an effective way to query the data source based on the user input. This is the tricky part. There are probably many ways to do this.Here are the most common

    * **Vector distance** between the user input and the data source. This is a concept used by most search engines. It works by create a vector representation of the user input and all your source  data. Then you calculate the distance between your user input vectors and all your source data vectors. The smaller the distance, the more similar the two vectors are. This is a very effective way to find similar documents. There are specialised data bases for this, like Pinecone, Elasticsearch, Redis and (Faiss).

4. Create a chatbot that uses the ChatGPT API and the data source.
    * Prompt engineering - Combine the user input with the data source to create a good prompt for the ChatGPT API. ChatGPT will be instructed to generate a response based on the data it is given.
The custom data is hidden from the user and only used to generate the prompt. The user will only see the ChatGPT API response