import os
import json
import chromadb
from groq import Groq
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS


### Vector DB functions
chroma_client = chromadb.PersistentClient(path="./vectordb")
collection = chroma_client.get_or_create_collection(name="atomcamp")

def load_data():
    f = open('scraped_data.json')
    data = json.load(f)
    for i in range(len(data)):
        collection.add(
                documents=[f"{data[i]['title']}\n{data[i]['text']}"],
                ids=[f"id_{i}"]
        )

def query_vectordb(user_message):
    context_response = collection.query(
        query_texts=[user_message],
        n_results=2
    )
    if context_response['documents']:
        context = "".join(context_response['documents'][0])
    else:
        context = "No relevant context found."
    return context

### LLM Inference with Groq
load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("GROQ_API_KEY not set in environment variables")

groq_client = Groq(api_key=api_key)

def chat_with_groq(user_message):
    context = query_vectordb(user_message)
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant called CampGuide. You work for AtomCamp. Answer all questions in a clear and concise manner.",
            },
            {
                "role": "user",
                "content": f"""Answer the following question, you may use the context above if needed:
                               
                               context:
                               {context}
                               question:
                               {user_message}"""
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

### Flask Server
app = Flask(__name__)
CORS(app)

@app.route('/')
def homepage():
    return render_template("index.html")

@app.route('/chat', methods=['GET'])
def chat():
    user_message = request.args.get('query')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    response = chat_with_groq(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)


