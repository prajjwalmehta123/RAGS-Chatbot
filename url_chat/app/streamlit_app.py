import streamlit as st
from scraper.web_crawler import WebCrawler
from vectorstore.vector_store import VectorStoreManager
from qa.question_answering import QuestionAnswering
from utils.config import Config

def main():
    st.title("Web Scraper with LangChain QA")

    # Initialize components
    crawler = WebCrawler()
    vector_store_manager = VectorStoreManager()
    qa_system = QuestionAnswering(Config.COHERE_API_KEY)

    # User inputs
    url_input = st.text_input("Enter the URL to crawl")
    rerank = st.checkbox("Use reranking", value=True)

    if st.button("Start Crawling"):
        if url_input:
            with st.spinner("Crawling website..."):
                folder_path = crawler.crawl_website(url_input)
            st.success(f"Crawling completed. Files saved to {folder_path}")

            with st.spinner("Creating vector store..."):
                vector_store = vector_store_manager.create_vector_store(folder_path)
            st.success("Vector store created.")

            query = st.text_input("Ask a question about the website content")

            if query:
                with st.spinner("Generating answer..."):
                    result = qa_system.get_answer(
                        query,
                        vector_store,
                        rerank=rerank
                    )
                    st.text_area("Answer:", result)
        else:
            st.error("Please enter a valid URL.")

if __name__ == "__main__":
    main()
