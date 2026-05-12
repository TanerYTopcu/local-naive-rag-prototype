import requests 
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import chromadb
from tools import scrapper,vectorizer

OLLAMA_CHAT = "http://localhost:11434/api/chat"

app = FastAPI(title="RAG ASSISTANT API")
chroma_client = chromadb.PersistentClient(path="./my_database")
collection = chroma_client.get_or_create_collection(name="wiki_bilgileri")

class ChatRequest(BaseModel):
    user_input : str
    memory: List[Dict]
@app.post("/ask")

def ask_assistant(request: ChatRequest):
    user_input = request.user_input
    memory = request.memory
    decision_prompt = """You are a strict keyword extraction API. Output ONLY valid JSON.
    Rule 1: If the user asks for info/facts, OR if the user simply types a noun/topic (e.g., "airplane", "apple", "quantum"), you MUST extract that noun as the query.
    Rule 2: Do NOT let chat history confuse you. If the latest message introduces a new noun/topic, extract it immediately and set search_required to true.
    
    Return format for ANY topic/noun:
    {"search_required": true, "query": "EntityName"}
    
    If and ONLY if the input is a pure greeting (e.g., "Hello", "How are you"), return:
    {"search_required": false, "query": ""}
    """
    decision_messages = [{"role": "system", "content": decision_prompt}] + memory + [{"role": "user", "content": user_input}]
    payload={
        "model":"llama3.2",
        "messages":decision_messages,
        "stream":False

    }
    try:
        response = requests.post(url=OLLAMA_CHAT,json=payload,timeout=10)
        result_str= response.json()["message"]["content"].strip()
        result_dict= json.loads(result_str)
        if result_dict.get("query") and result_dict.get("query").strip() != "":
            result_dict["search_required"] = True
        print(f"\n[DECISION ENGINE] {result_dict}")
    except Exception as e :
        return{"answer": str(e)}
    most_relevant=""
    system_prompt = {
                        "role": "system",
                        "content": "You are a helpful and friendly AI assistant. "
                        "Chat with the user naturally."
    }
    if result_dict["search_required"]== True:
            search_word = result_dict.get("query")
            db_results= collection.get(
                where={"subject":search_word}
            )
            if len(db_results["ids"]) >0:
                q_vector=vectorizer(user_input)
                search_result =collection.query(
                    query_embeddings=[q_vector],
                    n_results=1,
                    where={"subject": search_word}
                )
                most_relevant = search_result["documents"][0][0]
            else:
                text_scraped = scrapper(search_word)
                if text_scraped =="Not Found" or "Error" in text_scraped:
                    return{"answer": "There are no resources on that field"}
                all_parags = text_scraped.split(".")
                chunks=[]
                final_parag=""
                for parag in all_parags:
                    parag = parag.strip()
                    final_parag += parag +"."
                    if len(final_parag) >= 800:
                        chunks.append(final_parag.strip())
                        final_parag = ""
                if  final_parag.strip():
                    chunks.append(final_parag.strip())        

                for index,chunk in enumerate(chunks) :
                  vectorized_parag = vectorizer(chunk)
                  collection.add(
                      documents=[chunk],
                      embeddings=[vectorized_parag],
                      metadatas=[{"subject": search_word}],
                      ids=[f"{search_word}_parca_{index}"]
                  )
                q_vector = vectorizer(user_input)  
                search_result =collection.query(
                    query_embeddings=[q_vector],
                    n_results=3,
                    where={"subject": search_word}
                )
                most_relevant ="\n\n".join(search_result["documents"][0])  
            
            system_prompt = {
                        "role": "system",
                        "content": f"""You are a strict data-extraction assistant. 
                                       Your ONLY source of truth is the provided WEBSITE CONTENT.
                                       You must absolutely NOT use your internal training data or general knowledge.
                                       If the answer to the user's question cannot be found explicitly in the WEBSITE CONTENT, you MUST reply with exactly: "The text does not contain any information on this field.
                                       WEBSITE CONTENT: {most_relevant}"""
                        }
    final_rag_messages= [system_prompt]+ memory + [{"role": "user", "content": user_input}]   
    rag_payload={
            "model":"llama3.2",
            "messages" :final_rag_messages,
            "stream":False             
            }
            
    try:
        final_response= requests.post(url=OLLAMA_CHAT,json=rag_payload,timeout=10)
        final_result = final_response.json()["message"]["content"].strip()
        return {"answer": final_result}
    except Exception as e :
        return{"answer":f"There is something wrong in LLM model,{e}"}