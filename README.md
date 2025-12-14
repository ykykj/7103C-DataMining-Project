# **AI Agent CLI – Personal Assistant Agent**

A terminal-based AI Agent built with **LangChain**, **DeepSeek**, and Google Workspace APIs.
This assistant can generate study or interview preparation plans, interact with Gmail, upload files to Google Drive, and more — all through a clean **CLI interface**.

<p align="center">
  <img src="sample_cli.png" width="650">
</p>

---

## 🚀 **Features**

### **✓ Intelligent Plan Generation**

* Creates personalized study plans.
* Generates custom interview preparation outlines.

### **✓ Email Automation**

* Sends emails using your Gmail account.
* Searches your inbox using keyword-based queries.
* Extracts summaries and relevant information from email threads.


### **✓ Google Calendar**

* Can create calendar events with or without invited participants.
* Read and query calendar events within time ranges.

### **✓ Google Maps API Integration**

* Direct Google Maps API integration
* Search for places and points of interest
* Geocoding and reverse geocoding
* Directions with multiple travel modes
* Distance matrix calculations
* Nearby places search
* Supports both Chinese and English queries

### **✓ CLI Interface**

* Simple and intuitive command-line experience.
* No web UI or additional desktop software needed.

### **✓ LLM Reasoning with DeepSeek**

* Integrated with LangChain’s agent framework.
* Dynamically calls tools such as search or send email based on intent.
* Configurable to work with other OpenAI-compatible APIs.

---

## 🛠 **Tech Stack**

| Component                 | Description              |
| ------------------------- |--------------------------|
| **Python 3.10+**          | Main runtime             |
| **LangChain**             | Agent + Tools            |
| **DeepSeek**              | LLM model                |
| **Google Workspace APIs** | Gmail + Calendar         |
| **Google Maps API**       | Location & Navigation    |
| **Qweather**              | Weather Service          |
| **OAuth 2.0**             | Authentication           |
| **Rich**                  | CLI styling              |

---

## 📦 **Installation**

### **1. Clone the Repository**

```bash
git clone https://github.com/ykykj/7103C-DataMining-Project.git
cd 7103C-DataMining-Project
```

### **2. Create Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

Minimal example for `requirements.txt`:

```txt
langchain
langchain-openai
google-auth
google-auth-oauthlib
google-api-python-client
python-dotenv
rich
```

---

## 🔐 **Google OAuth Setup (Required)**

This project uses **OAuth 2.0 Client IDs** to authenticate with Google Services.

### **Steps:**

#### 1. Open Credential Creation Guide

Official Google guide:
[https://developers.google.com/workspace/guides/create-credentials](https://developers.google.com/workspace/guides/create-credentials)

#### 2. Configure OAuth Consent Screen

Required before you can create OAuth client credentials.

#### 3. Create OAuth Client ID

* Application type: **Desktop App**

#### 4. Get Client ID and Secret

After creating the OAuth client, copy the **Client ID** and **Client Secret**.
You will add these to your environment variables (see below).

---

## 🔑 **Environment Variables**

Create a `.env` file with the following variables:

```env
# DeepSeek API (for LLM)
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseek-chat

# Google Cloud OAuth
# Copy these from your Google Cloud Console
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Google Maps API (for location services)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Optional: Web Search
TAVILY_API_KEY=your_tavily_api_key
```

See `.env.example` for a complete configuration template.

### **Google Maps API Setup**

**Prerequisites:**
- Google Maps API Key

**Steps:**
1. Visit [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
2. Enable these APIs:
   - Places API
   - Geocoding API
   - Directions API
   - Distance Matrix API
4. Create an API key
5. Add it to your `.env` file



For detailed setup instructions, see `GOOGLE_MAPS_SETUP.md` or `QUICKSTART.md`.

---

## 📁 **Project Structure**

```
/
├── main.py                  # Entry Point
├── src/
│   ├── agent/             # Agent Logic
│   │   ├── __init__.py
│   │   └── PersonalAssistantAgent.py
│   │
│   ├── service/           # API Services
│   │   ├── __init__.py
│   │   ├── GoogleService.py
│   │   └── WeatherService.py
│   │
│   ├── tools/             # Agent Tools
│   │   ├── __init__.py
│   │   ├── AgentTools.py
│   │   └── GoogleMapTools.py
│   │
│   └── config.py          # Configuration
└── .env                   # Environment Variables
```

---

## ▶️ **Running the Application**

To start the CLI:

```bash
python main.py
```

---

## 🧩 **Future Enhancements**
* Voice command integration
* Automated multi-step workflows
* Optional FastAPI dashboard

---

## 📜 **License**

MIT License or any license you choose.

---
