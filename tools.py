from bs4 import BeautifulSoup
import requests 


OLLAMA_EMBED_CHAT ="http://localhost:11434/api/embeddings"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
def scrapper(subject):
    search_word = subject.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{search_word}" 

    response = requests.get(url, headers = HEADERS,timeout=10)
    try:
        if response.status_code != 200:
            return "Not Found"
        soup = BeautifulSoup(response.content,"html.parser")
        if soup.body:
            for unnec in soup.body(["script","style"]):
                unnec.decompose()
            text = soup.body.get_text(separator="\n", strip=True)
        else:
            text=""
        return(text)
    except Exception as e:
        return f"Error {e}"
    

def vectorizer(text):

    payload_vector={"model":"nomic-embed-text","prompt":text}
    response = requests.post(url=OLLAMA_EMBED_CHAT,json=payload_vector,timeout=10)
    if response.status_code != 200:
        print(f"\n[FATAL ERROR] Ollama API REFUSED THE EMBEDDINGS REQUEST!")
        print(f"Posted_Text: '{text}'")
        print(f"Server Response: {response.text}\n")
        exit()
    return response.json()["embedding"]

