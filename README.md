--------------------------Local Naive Rag Prototype - Wikipedia Searcher------------------

Note: Frontend of this app was built using AI via vibe coding.

----------------Tech Stack--------------

Backend : FastAPI
Frontend : Streamlit
Vector DB : ChromaDB
LLM : Llama 3.2 (Locally Hosted)
Scraping : BeautifulSoup4
---------------How It Works--------------
1. A Decision Engine (LLM) analyzes the user's prompt to determine if external facts are required.
2. If facts are needed, it extracts the main entity and scrapes Wikipedia.
3. The text is chunked, embedded, and stored in a local ChromaDB instance.
4. The most relevant chunks are retrieved and fed into the Llama 3.2 context window to generate a grounded response.
--------------Setup---------------------
1. Clone the repository and navigate to the directory
git clone https://github.com/TanerYTopcu/local-naive-rag-prototype.git
cd local-naive-rag-prototype
2. Install dependencies
Make sure you have Python installed. It is recommended to use a virtual environment.
pip install -r requirements.txt
3. Install and run Ollama
You need to have Ollama installed on your system to run the local LLM.
ollama run llama3.2
4. Run the backend
uvicorn api:app --reload
5. Run the frontend
streamlit run app.py