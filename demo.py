import streamlit as st 
import os
import openai
from llama_index import VectorStoreIndex, SimpleDirectoryReader , Document
from llama_index.embeddings import HuggingFaceEmbedding 
from llama_index import ServiceContext
from llama_index.llms import OpenAI

openai.api_key = st.secrets.openai_key 

st.title("📝 Passenger Car Emissions Q & A Chatbot ") 

with st.sidebar:
  st.write("""Document Name : PART 86—CONTROL OF EMISSIONS FROM NEW AND IN-USE HIGHWAY VEHICLES AND ENGINES \n 
                  Document URL: https://www.ecfr.gov/current/title-40/part-86""")
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Mention your queries!"}
    ]
    
llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3, system_prompt="""You are an expert in passenger car emission regulation.Answer
there queries about the regulations and the related details from the context given.Keep the answers technical and explain the details. Keep your answers accurate and based on 
                   facts – do not hallucinate features.""")

service_context = ServiceContext.from_defaults(llm=llm) 
documents=SimpleDirectoryReader(input_dir="./data/")
documents=documents.load_data() 
index = VectorStoreIndex.from_documents(documents, service_context=service_context)
index.storage_context.persist()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)


# if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
if prompt :=st.text_input("How can i help you today?",placeholder="Your query here",disabled= not documents):
    st.session_state.messages.append({"role": "user", "content": prompt})

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)
