# URL-based Chat Application

A web application that allows users to have interactive conversations about the content of any website. The application crawls the specified website, processes its content, and uses advanced language models to answer questions about the site's content.

## Features

- Web crawling and content extraction
- Vector-based document storage and retrieval
- Question-answering using Cohere's language models
- Content reranking for improved answer relevance
- User-friendly Streamlit interface

## Prerequisites

- Python 3.8+
- Cohere API key
- Installation of required packages

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/url-chat.git
cd url-chat
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Cohere API key:
```
COHERE_API_KEY=your_api_key_here
```

## Project Structure

```
url_chat/
│
├── scraper/               # Web crawling functionality
│   ├── __init__.py
│   └── web_crawler.py
│
├── vectorstore/          # Vector storage management
│   ├── __init__.py
│   └── vector_store.py
│
├── qa/                  # Question-answering system
│   ├── __init__.py
│   └── question_answering.py
│
├── app/                 # Streamlit application
│   ├── __init__.py
│   └── streamlit_app.py
│
├── utils/              # Utility functions and configuration
│   ├── __init__.py
│   └── config.py
│
└── requirements.txt    # Project dependencies
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app/streamlit_app.py
```

2. Enter a URL to crawl in the web interface.

3. Wait for the crawling and processing to complete.

4. Ask questions about the website's content through the interface.

## Component Details

### Web Crawler
- Handles website crawling and content extraction
- Manages visited URLs to avoid duplicates
- Saves extracted content to text files

### Vector Store Manager
- Creates and manages FAISS vector stores
- Handles document splitting and embedding
- Provides save and load functionality

### Question Answering System
- Utilizes Cohere's language models
- Implements content reranking for better answers
- Manages retrieval-augmented generation

## Acknowledgments

- [LangChain](https://github.com/hwchase17/langchain) for the chain-of-thought implementation
- [Cohere](https://cohere.ai/) for the language model and reranking capabilities
- [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search
- [Streamlit](https://streamlit.io/) for the web interface

## Note on Usage

Please ensure you have permission to crawl websites and comply with their robots.txt files and terms of service. This tool should be used responsibly and in accordance with website policies.