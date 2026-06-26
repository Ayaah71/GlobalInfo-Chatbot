# 🌍 GlobalInfo Chatbot

A full-stack conversational chatbot that provides rich information about countries worldwide — including capitals, populations, currencies, languages, regions, borders, timezones, and more — through a sleek, modern chat interface.

---

## 📌 Overview

GlobalInfo Chatbot lets users ask natural language questions about any country and receive instant, well-formatted answers. The app uses a free, open-source country dataset (no API key required) and presents information through an interactive, dark-mode chat UI.

---

## ✨ Features

- 🔍 Ask about **any country** in natural language
- 🏛️ Retrieve **capitals, populations, currencies, languages**
- 🌍 View **regions, continents, subregions**
- 🤝 Check **land borders** between countries
- ⏰ Look up **timezones** and **calling codes**
- 📐 Get **area/size** information
- 🏳️ See **flag emojis** and image links
- 💬 Conversational chatbot with greeting and help intents
- ⚡ FastAPI backend with automatic Swagger docs
- 📱 Responsive, mobile-friendly frontend with dark glassmorphism design
- 💡 12 quick-query chips in the sidebar for instant exploration

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Requests, Pydantic |
| **Frontend** | HTML5, CSS3 (Glassmorphism), Vanilla JavaScript |
| **Data Source** | [mledoze/countries](https://github.com/mledoze/countries) (free, no API key) |
| **Fonts** | Google Fonts — Inter |

---

## 📂 Project Structure

```
GlobalInfo-Chatbot/
│
├── Backend/
│   ├── main.py                    # FastAPI app — GET /country, POST /chat
│   ├── requiremnts.txt            # Python dependencies
│   └── services/
│       ├── __init__.py
│       ├── chatbot_service.py     # Intent detection & response generation
│       └── country_service.py    # Country data fetching & caching
│
├── Frontend/
│   ├── index.html                 # Chat UI layout
│   ├── style.css                  # Dark glassmorphism theme + animations
│   └── script.js                  # Chat logic, API calls, markdown rendering
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/GlobalInfo-Chatbot.git
cd GlobalInfo-Chatbot
```

### 2. Install Python Dependencies

> No virtual environment required — install globally or in your own venv.

```bash
pip install fastapi "uvicorn[standard]" requests pydantic
```

---

## ▶️ Running the Project

### Start the Backend

```bash
cd Backend
python -m uvicorn main:app --reload
```

| Endpoint | URL |
|----------|-----|
| Backend root | `http://127.0.0.1:8000` |
| Swagger API docs | `http://127.0.0.1:8000/docs` |
| Country data | `http://127.0.0.1:8000/country/{name}` |
| Chat endpoint | `POST http://127.0.0.1:8000/chat` |

### Start the Frontend

Open a second terminal and run:

```bash
cd Frontend
python -m http.server 5500
```

Then open **http://localhost:5500** in your browser.

> Alternatively, just double-click `Frontend/index.html` to open it directly.

---

## 💬 Example Queries

```
Tell me about Japan
What is the capital of France?
Population of India
Currency of Egypt
Languages spoken in Switzerland
Where is Brazil located?
Borders of Germany
Timezone of Australia
Area of Russia
Calling code of South Korea
Flag of Canada
```

---

## 📊 API Reference

### `GET /country/{country_name}`

Returns structured data for a country.

**Example response for `/country/Japan`:**
```json
{
  "name": "Japan",
  "official_name": "Japan",
  "capital": "Tokyo",
  "population": 125681593,
  "region": "Asia",
  "subregion": "Eastern Asia",
  "currencies": { "JPY": "Japanese yen" },
  "languages": ["Japanese"],
  "flag_emoji": "🇯🇵",
  "area": 377930,
  "timezones": ["UTC+09:00"],
  "borders": ["CHN", "PRK", "KOR"],
  "continents": ["Asia"],
  "calling_code": "+81"
}
```

### `POST /chat`

Accepts a natural language message and returns a conversational response.

**Request:**
```json
{ "message": "Capital of France" }
```

**Response:**
```json
{
  "response": "🇫🇷 The capital of **France** is **Paris**.",
  "intent": "capital",
  "data": { ... }
}
```

**Supported intents:** `capital` · `population` · `currency` · `language` · `region` · `flag` · `area` · `timezone` · `border` · `calling_code` · `general` · `greeting` · `help`

---

## 🗄️ Data Source

This project uses the **[mledoze/countries](https://github.com/mledoze/countries)** dataset — a free, open-source JSON file containing data for 250 countries. It requires no API key and is loaded once on startup and cached in memory.

> **Note:** The originally planned `restcountries.com` v3.1 API was deprecated in 2025 and now requires a paid subscription. This dataset is a free drop-in replacement with the same schema.

---

## 🚀 Future Enhancements

- [ ] Weather information integration
- [ ] Time zone support with live clocks
- [ ] Country flags and interactive maps
- [ ] Persistent chat history (localStorage)
- [ ] Voice interaction (Web Speech API)
- [ ] NLP-based intent recognition (spaCy / transformers)
- [ ] User authentication
- [ ] Database integration (PostgreSQL)
- [ ] Deployment (Render + Vercel)

---

## 🎯 Learning Objectives

This project demonstrates:

- REST API design with **FastAPI**
- Natural language **intent detection** (regex-based NLP)
- Frontend–backend communication via `fetch` API
- JSON data processing and transformation
- **Glassmorphism** UI design with CSS animations
- Full-stack web development workflow

---

## 🌐 Deployment
if you want to try it ( https://global-info-chatbot.vercel.app/ )

---

## 👩‍💻 Author

**Aya Mamdouh Ahmed**  
AI & Computer Science Graduate

**Interests:** Machine Learning · NLP · Recommender Systems · Software Development

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
