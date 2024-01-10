import streamlit as st
from dotenv import load_dotenv
import os
import openai
from llama_index import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index import ServiceContext
from llama_index.llms import OpenAI
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings

# Load environment variables from .env file
load_dotenv()

# Corrected the method to fetch environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

st.title("Soothsayer Analytics Chatbot")

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Mention your queries!"}
    ]

llm = OpenAI(system_prompt="""Your system prompt here...""",
             model="gpt-3.5-turbo",
             temperature=0.3)

service_context = ServiceContext.from_defaults(llm=llm)

urls = []  # You might want to add URLs here
loaders = UnstructuredURLLoader(urls=urls)
data = loaders.load()
text_splitter = CharacterTextSplitter(separator="\n", chunk_size=600, chunk_overlap=100)
documents = text_splitter.split_documents(data)
embeddings = OpenAIEmbeddings()

if "chat_engine" not in st.session_state.keys():
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    index.storage_context.persist()
    st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.text_input("How can I help you today?", placeholder="Your query here", disabled=not documents):
    prompt = "Provide the citations and elucidate the concepts of " + str(prompt) + ". Include detailed information from relevant sections and sub-sections to ensure a comprehensive response."
    st.session_state.messages.append({"role": "user", "content": prompt})

if st.session_state.messages[-1]["role"] != "assistant":
    with st.spinner("Thinking..."):
        response = st.session_state.chat_engine.chat(prompt)
        st.write(response.response)
        message = {"role": "assistant", "content": response.response}
        st.session_state.messages.append(message)
