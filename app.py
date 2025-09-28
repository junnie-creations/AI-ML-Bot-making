from flask import Flask, request, jsonify, render_template
from transformers import *
from sentence_transformers import SentenceTransformer, util
import sqlite3

app = Flask(__name__)

# Load NLP models
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli") # used for pretrained model designed for, load a pre-trained model, text-clssification/ sentiment analysis.
# zsc - technique that classify the text which it have not seen (facebook - pre trained language model/ ds: mnli/ used to classify the uncatecorized text)
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-medium")
# process and response the inputsb in humanize manner / combo of NLP and text generation and custom logic / DGPT medium: mid sized model / generate more natural and conventional text 

# Load Sentence Transformer for better matching
embedder = SentenceTransformer("all-MiniLM-L6-v2") # designed for vector representation / find similar text and clustering

# Static Responses
GREETING_RESPONSES = {
    "hi": "Hello! How can I assist you today?",
    "hello": "Hi there! What can I help you with?",
    "hey": "Hey! How’s your day going?",
    "bye": "Goodbye! Have a great day ahead!",
    "exit": "Take care! If you need guidance, I’m always here.",
    "what is your name": "I'm Vector, your career guidance assistant!"
}

# FAQ Database
FAQ_DB = {
    "career paths": "There are multiple career paths after Science. You can opt for Engineering, Medicine, Research, Data Science, etc.",
    "college options": "You can consider colleges based on your field of interest. Some top colleges for Science are IISc, IITs, NITs, AIIMS, etc.",
    "job roles": "Based on your skills, you can explore roles such as Software Engineer, Data Scientist, Doctor, Research Scientist, etc.",
    "commerce field": "If you take commerce, you can explore fields like Chartered Accountancy (CA), Business Administration, Banking, Finance, and Management.",
    "science field": "Science offers opportunities in fields like Engineering, Medicine, Data Science, Biotechnology, and Research.",
    "what are you": "I am Vector, the bot created for assisting you through your career paths.",
}

# Create embeddings for FAQ keys
faq_questions = list(FAQ_DB.keys()) # creating a list of embeding in FAQ keys
faq_embeddings = embedder.encode(faq_questions, convert_to_tensor=True) 

# Initialize SQLite database for feedback and escalations
DB_FILE = "feedback.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        response TEXT,
        rating TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS escalations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        status TEXT DEFAULT 'Pending'
    )
""")

conn.commit()
conn.close()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_query = data.get("query", "").strip().lower()

    # Check if the query is a greeting
    for greeting in GREETING_RESPONSES:
        if greeting in user_query:
            return jsonify({"response": GREETING_RESPONSES[greeting]})

    # Match FAQ using sentence similarity
    user_embedding = embedder.encode(user_query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(user_embedding, faq_embeddings)
    best_match_idx = similarities.argmax().item()
    confidence = similarities[0][best_match_idx].item()

    if confidence > 0.7:  # If confidence is high, use FAQ response
        response = FAQ_DB[faq_questions[best_match_idx]]
    else:
        # If no match, escalate the query
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO escalations (query, status) VALUES (?, 'Pending')", (user_query,))
        conn.commit()
        conn.close()
        response = "Your query has been escalated to a human agent. We will get back to you soon."

    return jsonify({"response": response})

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    query = data.get("query")
    response = data.get("response")
    rating = data.get("rating")

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (query, response, rating) VALUES (?, ?, ?)", (query, response, rating))
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"message": "Feedback recorded"})

@app.route("/analytics", methods=["GET"])
def analytics():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_queries = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating = 'thumbs_up'")
        positive_feedback = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating = 'thumbs_down'")
        negative_feedback = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM escalations WHERE status = 'Pending'")
        pending_escalations = cursor.fetchone()[0] if cursor.fetchone() else 0
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({
        "total_queries": total_queries,
        "positive_feedback": positive_feedback,
        "negative_feedback": negative_feedback,
        "pending_escalations": pending_escalations
    })

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)