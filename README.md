# 🌍 GlobalInfo Chatbot

A web-based chatbot that provides global information about countries — including capitals, populations, currencies, languages, and regions — through a simple conversational interface.

---

## 📌 Overview

GlobalInfo Chatbot helps users quickly access country-related information using natural language queries. The application integrates public APIs and presents information in an interactive chat format.

---

## ✨ Features

- 🔍 Search information about any country
- 🏛️ Retrieve capitals, populations, and currencies
- 🗣️ View official languages and geographic regions
- 💬 Conversational chatbot interface
- ⚡ FastAPI backend with REST API integration
- 📱 Responsive and lightweight frontend

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, Requests |
| **Frontend** | HTML5, CSS3, JavaScript |
| **External API** | [REST Countries API](https://restcountries.com) |

---

## 📂 Project Structure

```
global-info-chatbot/
│
├── backend/
│   ├── main.py
│   ├── services/
│   │   ├── chatbot_service.py
│   │   └── country_service.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/global-info-chatbot.git
cd global-info-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

### Start the Backend

```bash
cd backend
uvicorn main:app --reload
```

| Endpoint | URL |
|----------|-----|
| Backend | `http://127.0.0.1:8000` |
| API Docs | `http://127.0.0.1:8000/docs` |

### Start the Frontend

Open `frontend/index.html` directly in your browser, or serve it locally:

```bash
python -m http.server 5500
```

Then navigate to `http://localhost:5500`.

---

## 💬 Example Queries

```
Tell me about Egypt
What is the capital of France?
Population of Canada
Currency of Japan
Languages spoken in Germany
```

---

## 📊 Sample Response

```json
{
  "country": "Egypt",
  "capital": "Cairo",
  "population": 114535772,
  "currency": "EGP"
}
```

---

## 📸 Screenshots

> _Add project screenshots here._

**Home Page**

<!-- ![Home Page](screenshots/home.png) -->

**Chat Example**

<!-- ![Chat Example](screenshots/chat.png) -->

---

## 🚀 Future Enhancements

- [ ] Weather information integration
- [ ] Time zone support
- [ ] Country flags and maps
- [ ] Persistent chat history
- [ ] Voice interaction
- [ ] User authentication
- [ ] Database integration
- [ ] NLP-based intent recognition

---

## 🎯 Learning Objectives

This project demonstrates:

- REST API integration
- FastAPI backend development
- Frontend–backend communication
- JSON data processing
- Full-stack web development workflow

---

## 🌐 Deployment

| Layer | Platform |
|-------|----------|
| Backend | [Render](https://render.com) |
| Frontend | [Vercel](https://vercel.com) |

---

## 👩‍💻 Author

**Aya Mamdouh Ahmed**  
AI & Computer Science Graduate

**Interests:** Machine Learning · NLP · Recommender Systems · Software Development

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
