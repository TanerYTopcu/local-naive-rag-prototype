import streamlit as st
import requests


API_URL = "http://localhost:8000/ask"
st.set_page_config(page_title="RAG Assistant", page_icon="🧠")
st.title("Wikipedia AI Research Assistant ")

if "memory" not in st.session_state:
    st.session_state.memory = []

for message in st.session_state.memory:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask me something or give me a field you want to know.")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.memory.append({"role": "user", "content": user_input})

    payload = {
        "user_input": user_input,
        "memory": st.session_state.memory[:-1] 
    }

    with st.spinner("Engines working, reasearching..."):
        try:
            
            response = requests.post(API_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                answer = response.json().get("answer", "Answer couldnt read.")
                
                with st.chat_message("assistant"):
                    st.markdown(answer)
                
                st.session_state.memory.append({"role": "assistant", "content": answer})
            else:
                st.error(f"API Error: Server returned this code block {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot access the backend server! Make sure FastAPI (uvicorn) is open ")
        except requests.exceptions.Timeout:
            st.error("Proccess timed out.")
