import streamlit as st 
import os
import openai
from llama_index import VectorStoreIndex, SimpleDirectoryReader , Document
from llama_index import ServiceContext
from llama_index.llms import OpenAI

openai.api_key = st.secrets.openai_key 

st.title("📝 Emission Control for New and In-Use Highway Vehicles Q & A Chatbot ") 

with st.sidebar:
  st.write("""Document Name : PART 86—CONTROL OF EMISSIONS FROM NEW AND IN-USE HIGHWAY VEHICLES AND ENGINES \n 
  Document Link: https://drafting.ecfr.gov/current/title-40/part-86""")

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Mention your queries!"}
    ]
    

llm=OpenAI(system_prompt="""Explore inquiries regarding regulations in PART 86—CONTROL OF EMISSIONS FROM NEW AND 
IN-USE HIGHWAY VEHICLES AND ENGINES within the Code of Federal Regulations. Cite the sub-part, sections, 
and sub-sections containing relevant information and answer the query by using the respective information. Provide fact-based and accurate responses,
avoiding speculative details.""",model="gpt-3.5-turbo",temperature=0.3)


service_context = ServiceContext.from_defaults(llm=llm) 
documents=SimpleDirectoryReader(input_dir="./data/")
documents=documents.load_data() 

if "chat_engine" not in st.session_state.keys():# Initialize the chat engine
  index = VectorStoreIndex.from_documents(documents, service_context=service_context)
  index.storage_context.persist()
  st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
  

if prompt :=st.text_input("How can i help you today?",placeholder="Your query here",disabled= not documents):
  prompt="Provide the citations and elucidate the concepts of"+str(prompt)+"Include detailed information from relevant sections and sub-sections to ensure a comprehensive response."
  st.session_state.messages.append({"role": "user", "content": prompt})

    
# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)
