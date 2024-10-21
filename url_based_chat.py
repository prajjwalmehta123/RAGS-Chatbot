# -*- coding: utf-8 -*-
"""URL based Chat.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1uB9pDN2Os6rWy7l95UY4ZYJ1onAqjVy5

# Installation
"""

!huggingface-cli login

!pip install -U langchain-community

!pip install streamlit unstructured requests beautifulsoup4 urllib3 faiss-cpu transformers sentence-transformers langchain accelerate bitsandbytes cohere langchain-cohere

"""# Scraper(Ignore)"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

# Set to keep track of visited URLs
visited_urls = set()

def get_all_links(url, base_domain):
    try:
        # Make a GET request to fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize an empty list to store the links found on this page
    links = []

    # Find all <a> tags with href attributes in the page
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        # Join the base URL with the href to handle relative URLs
        full_link = urljoin(url, link)

        # Check if the domain of the link matches the base domain
        link_domain = urlparse(full_link).netloc
        if link_domain == base_domain and full_link not in visited_urls:
            links.append(full_link)

    return links

def save_page_content(url, folder_path):
    try:
        # Make a GET request to fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the page text
    page_text = soup.get_text(separator=' ', strip=True)

    # Create a file name based on the URL's path
    parsed_url = urlparse(url)
    file_name = parsed_url.path.strip('/').replace('/', '_') or 'home'
    file_path = os.path.join(folder_path, f"{file_name}.txt")

    # Save the text content to a .txt file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(page_text)
        print(f"Saved content from {url} to {file_path}")
    except Exception as e:
        print(f"Failed to save content from {url}: {e}")

def crawl_website(url):
    # Parse the base domain from the input URL
    base_domain = urlparse(url).netloc

    # Create a folder with the base domain name to store the content
    folder_path = os.path.join(os.getcwd(), base_domain)
    os.makedirs(folder_path, exist_ok=True)

    # Recursively search and collect links within the same domain
    def recursive_crawl(current_url):
        if current_url in visited_urls:
            return
        visited_urls.add(current_url)

        # Get all internal links from the current page
        links = get_all_links(current_url, base_domain)

        # Save the page content to a .txt file
        save_page_content(current_url, folder_path)

        for link in links:
            if link not in visited_urls:
                recursive_crawl(link)  # Recursively crawl the new link

    # Start crawling from the initial URL
    recursive_crawl(url)

if __name__ == "__main__":
    # Input the URL
    start_url = input("Enter the URL to crawl: ").strip()

    # Start the crawling process
    crawl_website(start_url)

    # Print all the visited links
    print(f"\nCrawling completed. Total links found: {len(visited_urls)}")
    for link in visited_urls:
        print(link)
# https://www.web-scraping.dev/

"""# Create vector store (Ignore)"""

from langchain.vectorstores import FAISS
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
# import nltk
# nltk.download('punkt')

# Load text files from a directory
loader = DirectoryLoader('/content/www.web-scraping.dev', loader_cls=TextLoader)
documents = loader.load()

# Split text into chunks (optional, depending on your document length)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = text_splitter.split_documents(documents)

# Create embeddings with Hugging Face
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create FAISS vector store
vector_store = FAISS.from_documents(split_docs, embeddings)

# Save FAISS index and document metadata
vector_store.save_local("faiss_store")

from langchain.chains import RetrievalQA
from langchain.llms import Cohere
from langchain.prompts import PromptTemplate

# Load FAISS store
vector_store = FAISS.load_local("faiss_store", embeddings, allow_dangerous_deserialization = True)

# Initialize the LLM (Cohere in this case)
from google.colab import userdata
COHERE_KEY = userdata.get('COHERE_KEY')
os.environ['COHERE_API_KEY'] = COHERE_KEY
llm = Cohere()

# Create the QA Chain
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_store.as_retriever())

# Perform a query
query = "What is the webpage about?"
result = qa_chain.run(query)
print(result)

"""# Scraper(Working)"""

# prompt: supress warnings

import warnings
warnings.filterwarnings('ignore')

# Required imports
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from langchain.vectorstores import FAISS
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.chains import RetrievalQA
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from langchain.llms import HuggingFacePipeline
import cohere

# --- Scraper Code ---
visited_urls = set()

def get_all_links(url, base_domain):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        full_link = urljoin(url, link)
        link_domain = urlparse(full_link).netloc
        if link_domain == base_domain and full_link not in visited_urls:
            links.append(full_link)

    return links

def save_page_content(url, folder_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text(separator=' ', strip=True)
    parsed_url = urlparse(url)
    file_name = parsed_url.path.strip('/').replace('/', '_') or 'home'
    file_path = os.path.join(folder_path, f"{file_name}.txt")

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(page_text)
        print(f"Saved content from {url} to {file_path}")
    except Exception as e:
        print(f"Failed to save content from {url}: {e}")

def crawl_website(url):
    base_domain = urlparse(url).netloc
    folder_path = os.path.join(os.getcwd(), base_domain)
    os.makedirs(folder_path, exist_ok=True)

    def recursive_crawl(current_url):
        if current_url in visited_urls:
            return
        visited_urls.add(current_url)
        links = get_all_links(current_url, base_domain)
        save_page_content(current_url, folder_path)

        for link in links:
            if link not in visited_urls:
                recursive_crawl(link)

    recursive_crawl(url)

if __name__ == "__main__":
    start_url = input("Enter the URL to crawl: ").strip()
    crawl_website(start_url)
    print(f"\nCrawling completed. Total links found: {len(visited_urls)}")
    for link in visited_urls:
        print(link)

# --- Create Vector Store ---

# Load text files from a directory
# Extract the base domain and create the folder dynamically
base_domain = urlparse(start_url).netloc  # This extracts the domain from the URL
folder_path = os.path.join(os.getcwd(), base_domain)  # Create the path dynamically

# Load text files from the dynamically created directory
loader = DirectoryLoader(folder_path, loader_cls=TextLoader)
documents = loader.load()

# Split text into chunks (optional, depending on your document length)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = text_splitter.split_documents(documents)

# Create embeddings with Hugging Face
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create FAISS vector store
vector_store = FAISS.from_documents(split_docs, embeddings)

# Save FAISS index and document metadata
vector_store.save_local("faiss_store")

# --- Use Llama 3.1 Quantized Model with LangChain ---
# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_quant_type="nf4",
#     bnb_4bit_use_double_quant=True,
#     bnb_4bit_compute_dtype="float16"
# )

model_name = "facebook/bart-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
llama_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    # quantization_config=bnb_config,
    device_map="auto"
)

# Create the LangChain-compatible LLM pipeline
from transformers import pipeline
llm_pipeline = pipeline("text-generation", model=llama_model, tokenizer=tokenizer, max_length = 512, max_new_tokens = 512)
llm = HuggingFacePipeline(pipeline=llm_pipeline)

from google.colab import userdata
COHERE_API_KEY = userdata.get('COHERE_API_KEY')
os.environ['COHERE_API_KEY'] = COHERE_API_KEY
# COHERE_API_KEY = "YOUR_COHERE_API_KEY"  # Remove this line or replace with your actual key
cohere_client = cohere.Client(COHERE_API_KEY)

def rerank_results(query, docs):
    rerank_response = cohere_client.rerank(
        query=query,
        documents=docs,
        top_n=len(docs)
    )
    # Access the 'results' attribute from the response
    results = rerank_response.results
    # Sort the results by relevance score in descending order
    sorted_results = sorted(results, key=lambda x: x.relevance_score, reverse=True)
    # Return the documents in the reranked order
    # print([docs[result.index] for result in sorted_results])
    return [docs[result.index] for result in sorted_results]

# --- LangChain QA Chain ---

from langchain.prompts import PromptTemplate
from langchain_cohere import CohereRerank
from langchain.chains import RetrievalQA
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_community.llms import Cohere

llm = Cohere(temperature=0)

# # Function for question-answer chain using LangChain
def question_answer_chain(query, k=3, rerank=True, llm = llm):
    # Step 1: Retrieve top-k documents from FAISS
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
    docs = retriever.get_relevant_documents(query)

    # Step 2: Optionally rerank using Cohere
    if rerank:
        compressor = CohereRerank(model="rerank-english-v3.0")
        compression_retriever = ContextualCompressionRetriever(
                        base_compressor=compressor, base_retriever=retriever)
        # Step 3: Use the QA chain from LangChain with Llama model
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=compression_retriever)
    else:
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    # Step 4: Generate the final answer using the QA chain
    answer = qa_chain.run(query)
    return answer

query = "are there skincare offerings?"

# Example query

result = question_answer_chain(query, k=3, rerank=True, llm = Cohere(temperature=0))
print(f"Summarized Answer: {result}")

# Example query

result = question_answer_chain(query, k=3, rerank=False, llm = Cohere(temperature=0))
print(f"Summarized Answer: {result}")



"""# Streamlit App(WIP)"""

# Commented out IPython magic to ensure Python compatibility.
# %%writefile chaturl.py
# 
# import streamlit as st
# import requests
# from urllib.parse import urlparse
# from langchain.vectorstores import FAISS
# from langchain.embeddings.huggingface import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import DirectoryLoader, TextLoader
# from langchain.chains import RetrievalQA
# from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
# from langchain.llms import HuggingFacePipeline
# import cohere
# import os
# from google.colab import userdata
# COHERE_API_KEY = userdata.get('COHERE_API_KEY')
# os.environ['COHERE_API_KEY'] = COHERE_API_KEY
# cohere_client = cohere.Client(COHERE_API_KEY)
# 
# 
# # --- Function to crawl the website ---
# def crawl_website(url):
#     visited_urls = set()
#     base_domain = urlparse(url).netloc
#     folder_path = os.path.join(os.getcwd(), base_domain)
#     os.makedirs(folder_path, exist_ok=True)
# 
#     def get_all_links(current_url, base_domain):
#         try:
#             response = requests.get(current_url)
#             response.raise_for_status()
#         except requests.exceptions.RequestException as e:
#             return []
#         soup = BeautifulSoup(response.text, 'html.parser')
#         links = []
#         for a_tag in soup.find_all('a', href=True):
#             link = a_tag['href']
#             full_link = urljoin(current_url, link)
#             link_domain = urlparse(full_link).netloc
#             if link_domain == base_domain and full_link not in visited_urls:
#                 links.append(full_link)
#         return links
# 
#     def save_page_content(current_url, folder_path):
#         try:
#             response = requests.get(current_url)
#             response.raise_for_status()
#         except requests.exceptions.RequestException as e:
#             return
#         soup = BeautifulSoup(response.text, 'html.parser')
#         page_text = soup.get_text(separator=' ', strip=True)
#         file_name = urlparse(current_url).path.strip('/').replace('/', '_') or 'home'
#         file_path = os.path.join(folder_path, f"{file_name}.txt")
#         try:
#             with open(file_path, 'w', encoding='utf-8') as f:
#                 f.write(page_text)
#         except Exception as e:
#             return
# 
#     def recursive_crawl(current_url):
#         if current_url in visited_urls:
#             return
#         visited_urls.add(current_url)
#         links = get_all_links(current_url, base_domain)
#         save_page_content(current_url, folder_path)
#         for link in links:
#             if link not in visited_urls:
#                 recursive_crawl(link)
# 
#     recursive_crawl(url)
#     return folder_path
# 
# 
# # Function to create a vector store using FAISS
# def create_vector_store(folder_path):
#     loader = DirectoryLoader(folder_path, loader_cls=TextLoader)
#     documents = loader.load()
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     split_docs = text_splitter.split_documents(documents)
#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#     vector_store = FAISS.from_documents(split_docs, embeddings)
#     return vector_store
# 
# 
# # Function for question-answer chain using LangChain
# def question_answer_chain(query, vector_store, rerank=True, llm=None):
#     retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
#     if rerank:
#         compressor = CohereRerank(model="rerank-english-v3.0")
#         compression_retriever = ContextualCompressionRetriever(
#             base_compressor=compressor, base_retriever=retriever
#         )
#         qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=compression_retriever)
#     else:
#         qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
#     answer = qa_chain.run(query)
#     return answer
# 
# 
# # --- Streamlit Interface ---
# st.title("Web Scraper with LangChain QA")
# 
# # Step 1: User input for the URL to crawl
# url_input = st.text_input("Enter the URL to crawl")
# 
# # Step 2: Option to enable/disable reranking
# rerank = st.checkbox("Use reranking", value=True)
# 
# # Step 3: Start the crawling process if the user enters a URL
# if st.button("Start Crawling"):
#     if url_input:
#         with st.spinner("Crawling website..."):
#             folder_path = crawl_website(url_input)
#         st.success(f"Crawling completed. Files saved to {folder_path}")
# 
#         # Step 4: Create Vector Store
#         with st.spinner("Creating vector store..."):
#             vector_store = create_vector_store(folder_path)
#         st.success("Vector store created.")
# 
#         # Step 5: Input field for the user to ask questions
#         query = st.text_input("Ask a question about the website content")
# 
#         # Step 6: Process the query
#         if query:
#             with st.spinner("Generating answer..."):
#                 # Set up a model (example: facebook/bart-large)
#                 # model_name = "facebook/bart-large"
#                 # tokenizer = AutoTokenizer.from_pretrained(model_name)
#                 # model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
#                 # qa_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=512, max_new_tokens=512)
#                 # llm = HuggingFacePipeline(pipeline=qa_pipeline)
# 
#                 # Generate the answer using the question-answer chain
#                 result = question_answer_chain(query, vector_store, rerank=rerank, llm=Cohere(temperature=0))
#                 st.text_area("Answer:", result)
#     else:
#         st.error("Please enter a valid URL.")
#

"""# Running Streamlit App(WIP)"""

!npm install localtunnel

import urllib
print("Password/Enpoint IP for localtunnel is:",urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip("\n"))

!streamlit run chatpdf.py &>/content/logs.txt &

!npx localtunnel --port 8501

"""# Demo(WIP)"""

import requests
from urllib.parse import urlparse, urljoin
from langchain.vectorstores import FAISS
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.chains import RetrievalQA
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from langchain.llms import HuggingFacePipeline
import cohere
import os
from bs4 import BeautifulSoup

# Load Cohere API key
from google.colab import userdata
COHERE_API_KEY = userdata.get('COHERE_API_KEY')
os.environ['COHERE_API_KEY'] = COHERE_API_KEY
cohere_client = cohere.Client(COHERE_API_KEY)

# --- Function to crawl the website ---
def crawl_website(url):
    visited_urls = set()
    base_domain = urlparse(url).netloc
    folder_path = os.path.join(os.getcwd(), base_domain)
    os.makedirs(folder_path, exist_ok=True)

    def get_all_links(current_url, base_domain):
        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {current_url}: {e}")
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            full_link = urljoin(current_url, link)
            link_domain = urlparse(full_link).netloc
            if link_domain == base_domain and full_link not in visited_urls:
                links.append(full_link)
        return links

    def save_page_content(current_url, folder_path):
        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {current_url}: {e}")
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ', strip=True)
        file_name = urlparse(current_url).path.strip('/').replace('/', '_') or 'home'
        file_path = os.path.join(folder_path, f"{file_name}.txt")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page_text)
        except Exception as e:
            print(f"Failed to save content from {current_url}: {e}")

    def recursive_crawl(current_url):
        if current_url in visited_urls:
            return
        visited_urls.add(current_url)
        links = get_all_links(current_url, base_domain)
        save_page_content(current_url, folder_path)
        for link in links:
            if link not in visited_urls:
                recursive_crawl(link)

    recursive_crawl(url)
    return folder_path


# Function to create a vector store using FAISS
def create_vector_store(folder_path):
    loader = DirectoryLoader(folder_path, loader_cls=TextLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(split_docs, embeddings)
    return vector_store


# Function for question-answer chain using LangChain
def question_answer_chain(query, vector_store, rerank=True, llm=None):
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    if rerank:
        compressor = cohere_rerank(query, docs)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=compression_retriever)
    else:
        qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
    answer = qa_chain.run(query)
    return answer


# Use Cohere's Rerank model
def cohere_rerank(query, docs):
    rerank_response = cohere_client.rerank(query=query, documents=docs, top_n=len(docs))
    results = rerank_response.results
    sorted_results = sorted(results, key=lambda x: x.relevance_score, reverse=True)
    return [docs[result.index] for result in sorted_results]


# --- Main logic (to run in Colab) ---
url_input = input("Enter the URL to crawl: ").strip()
use_rerank = input("Use reranking? (yes/no): ").lower() == "yes"

# Step 1: Start Crawling
print(f"Starting crawl for {url_input}...")
folder_path = crawl_website(url_input)
print(f"Crawling completed. Files saved to {folder_path}")

# Step 2: Create Vector Store
print("Creating vector store...")
vector_store = create_vector_store(folder_path)
print("Vector store created.")

# Step 3: Ask a question
query = input("Ask a question about the website content: ").strip()

# Step 4: Setup LLM (using BART in this example)
# model_name = "facebook/bart-large"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
# qa_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=512, max_new_tokens=512)
# llm = HuggingFacePipeline(pipeline=qa_pipeline)

# Step 5: Get the answer
if query:
    print("Generating answer...")
    result = question_answer_chain(query, vector_store, rerank=use_rerank, llm=llm)
    print(f"Answer: {result}")
else:
    print("Please enter a valid query.")

