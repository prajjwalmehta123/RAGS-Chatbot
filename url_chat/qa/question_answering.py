from langchain.chains import RetrievalQA
from langchain_cohere import Cohere, CohereRerank
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever

class QuestionAnswering:
    def __init__(self, api_key):
        self.llm = Cohere(cohere_api_key=api_key, temperature=0)

    def get_answer(self, query, vector_store, k=3, rerank=True):
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

        if rerank:
            compressor = CohereRerank(model="rerank-english-v3.0")
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=retriever
            )
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=compression_retriever
            )
        else:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever
            )

        return qa_chain.run(query)