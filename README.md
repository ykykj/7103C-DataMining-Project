# **AI Agent CLI – Personal Assistant Agent**

A terminal-based AI Agent built with **LangChain**, **Google Gemini 2.5 Pro**, and Google Workspace APIs.
This assistant can generate study or interview preparation plans, interact with Gmail, upload files to Google Drive, and more — all through a clean **CLI interface**.

<p align="center">
  <img src="sample_cli.png" width="650">
</p>

---

## 🚀 **Features**

### **✓ Intelligent Plan Generation**

* Creates personalized study plans.
* Generates custom interview preparation outlines.
* Outputs can be stored directly in Google Drive.

### **✓ Email Automation**

* Sends emails using your Gmail account.
* Searches your inbox using keyword-based queries.
* Extracts summaries and relevant information from email threads.

### **✓ Google Drive Integration**

* Uploads generated files to Drive.
* Allows Drive-based workflows through the agent.

### **✓ Google Calendar**

* Can create calendar events with or without invited participants.
* Read and query calendar events within time ranges.

### **✓ Google Maps MCP Integration**

* Official Google Maps MCP Server integration
* Search for places and points of interest
* Geocoding and reverse geocoding
* Directions with multiple travel modes
* Distance matrix calculations
* Nearby places search
* Supports both Chinese and English queries
* Automatic tool discovery via MCP protocol

### **✓ CLI Interface**

* Simple and intuitive command-line experience.
* No web UI or additional desktop software needed.

### **✓ LLM Reasoning with Gemini 2.5 Pro**

* Integrated with LangChain’s agent framework.
* Dynamically calls tools such as search, send email, or upload to Drive based on intent.

---

## 🛠 **Tech Stack**

| Component                 | Description              |
| ------------------------- |--------------------------|
| **Python 3.10+**          | Main runtime             |
| **LangChain**             | Agent + Tools            |
| **Google Gemini 2.5 Pro** | LLM model                |
| **Google Workspace APIs** | Gmail + Drive + Calendar |
| **Google Maps MCP**       | Location & Navigation    |
| **MCP Protocol**          | Tool Integration         |
| **OAuth 2.0**             | Authentication           |
| **Rich**                  | CLI styling              |

---

## 📦 **Installation**

### **1. Clone the Repository**

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
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
google-generativeai
google-auth
google-auth-oauthlib
google-api-python-client
python-dotenv
rich
```

---

## 🔐 **Google OAuth Setup (Required)**

This project **requires a `credentials.json`** file downloaded from Google Cloud Console.

### **Steps:**

#### 1. Open Credential Creation Guide

Official Google guide:
[https://developers.google.com/workspace/guides/create-credentials](https://developers.google.com/workspace/guides/create-credentials)

#### 2. Configure OAuth Consent Screen

Required before you can create OAuth client credentials.

#### 3. Create OAuth Client ID

* Application type: **Desktop App**

#### 4. Download JSON File

After creating the OAuth client, click **Download JSON**.

#### 5. Place the File in the Required Folder

Your project must contain:

```
creds/credentials.json
```

The application loads OAuth credentials from this file.

---

## 🔑 **Environment Variables**

Create a `.env` file with the following variables:

```env
# DeepSeek API (for LLM)
DEEPSEEK_API_KEY=your_deepseek_api_key

# Google Cloud
GOOGLE_CLOUD_AUTH_EMAIL=your-email@gmail.com
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Google Maps API (for location services)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Optional: Web Search
TAVILY_API_KEY=your_tavily_api_key
```

See `.env.example` for a complete configuration template.

### **Google Maps MCP Setup**

**Prerequisites:**
- Node.js and npm (for running MCP server)

**Steps:**
1. Install Node.js from [nodejs.org](https://nodejs.org/)
2. Visit [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
3. Enable these APIs:
   - Places API
   - Geocoding API
   - Directions API
   - Distance Matrix API
4. Create an API key
5. Add it to your `.env` file

**Quick Start:**
```bash
# Run installation script
install_google_maps.bat  # Windows
# or
./install_google_maps.ps1  # PowerShell

# Test configuration
python test_google_maps.py
```

For detailed setup instructions, see `GOOGLE_MAPS_SETUP.md` or `QUICKSTART.md`.

---

## 📁 **Project Structure**

This README follows **your exact structure**, as provided:

```
src/
├── agent/
│   ├── __init__.py
│   └── PersonalAssistantAgent.py
│
├── service/
│   ├── __init__.py
│   └── GoogleService.py
│
├── tools/
│   ├── __init__.py
│   └── AgentTools.py
│
└── Main.py
```

Additionally, you must manually create:

```
creds/
└── credentials.json
```
---

## ▶️ **Running the Application**

To start the CLI:

```bash
python -m src.Main.py
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
