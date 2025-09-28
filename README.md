# AI-ML-Bot-making
This is the code for AI/ML bot creation and can be used as project based profile building. Free to use template and public accessable code.

# 🎯 AI-Powered Career Guidance Chatbot

An **AI-driven career guidance chatbot** built with Flask and NLP models to assist users with career-related queries.  
It provides predefined answers, processes free-form questions, collects feedback, escalates complex queries, and tracks performance using analytics.

---

## 📖 Project Report

### 1. Introduction
This project presents an AI-powered career guidance chatbot designed to:
- Answer career-related queries using predefined FAQs.
- Process free-form questions with NLP models.
- Escalate complex queries to human agents.
- Collect user feedback and track performance analytics.

---

### 2. Project Goals
- ✅ Create an intelligent chatbot for career assistance.  
- ✅ Use NLP for answering FAQs.  
- ✅ Escalate queries requiring human intervention.  
- ✅ Collect user feedback for continuous improvement.  
- ✅ Track performance and engagement via analytics.  

---

### 3. Technology Stack
- **Backend:** Flask (Python)  
- **NLP Models:** Hugging Face Transformers  
  - Facebook BART  
  - Microsoft DialoGPT  
- **Embedding Model:** Sentence Transformers (`all-MiniLM-L6-v2`)  
- **Database:** SQLite (Feedback + Escalations)  
- **Frontend:** HTML (Flask Templates)  

---

### 4. Features & Functionality
#### 💬 Chatbot Responses
- Matches user queries with Sentence Transformers.  
- Retrieves closest FAQ-based response.  
- Escalates low-confidence queries.  

#### 🚨 Escalation Handling
- Stores unresolved queries in SQLite.  
- Notifies users about escalation.  

#### 👍👎 Feedback Collection
- Users can rate chatbot responses.  
- Feedback stored in database for review.  

#### 📊 Analytics & Tracking
- Tracks total queries handled.  
- Logs positive/negative feedback.  
- Monitors pending escalations.  

---

### 5. Code Overview

#### 🔑 Key API Endpoints
```python
POST   /chat       # Process user queries and return chatbot response
POST   /feedback   # Store feedback (thumbs up/down)
GET    /analytics  # Retrieve performance metrics
GET    /           # Render chatbot interface

# 🗄️ Database Structure

```sql
-- Feedback Table
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_query TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    rating TEXT CHECK(rating IN ('up', 'down'))
);

-- Escalations Table
CREATE TABLE escalations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_query TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
