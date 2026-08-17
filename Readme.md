# 🌱 AgroTech WhatsApp AI

### AI-Powered Crop Disease Detection & Farmer Assistance Through WhatsApp

**AgroTech WhatsApp AI** is a production-oriented **multimodal AI assistant for farmers** that allows users to send crop images and questions directly through **WhatsApp**. The system analyzes the uploaded crop image using a vision-capable LLM, combines visual information with contextual knowledge using **Retrieval-Augmented Generation (RAG)**, and returns an actionable response to the farmer through WhatsApp.

The project is built with **FastAPI, LangGraph, Groq, Supabase/PostgreSQL, Meta WhatsApp Cloud API, and multimodal LLMs** and is deployed as a cloud-based backend.

---

## Why This Project?

Farmers often face difficulties identifying crop diseases quickly and accessing agricultural expertise.

Instead of requiring a separate application, AgroTech brings AI assistance directly to a platform farmers already use:

**Send a crop photo → Ask a question → Receive an AI-powered analysis.**

The system is designed around:

* Image-based crop analysis
* Multimodal LLM reasoning
* Retrieval-Augmented Generation (RAG)
* WhatsApp conversational interface
* LangGraph workflow orchestration
* Supabase/Qdrant persistence
* FastAPI backend
* Cloud deployment

---

# ✨ Key Features

### Multimodal Crop Analysis

Farmers can send a crop image through WhatsApp.

The system:

1. Receives the WhatsApp webhook event.
2. Extracts the media ID.
3. Retrieves the image from Meta's Graph API.
4. Converts the image into a model-compatible representation.
5. Sends the image to the AI workflow.
6. Generates a crop/disease analysis.

---

### AI-Powered Question Answering

Users can ask questions such as:

```text
What disease is affecting my tomato plant?
```

or send:

```text
[Crop Image]

What should I do to treat this?
```

The assistant generates contextual responses rather than returning only a classification label.

---

### Retrieval-Augmented Generation

The system can incorporate agricultural knowledge using **RAG** to improve contextual relevance and reduce unsupported responses.

Conceptually:

```text
User Question + Crop Image
          ↓
      AI Workflow
          ↓
   Retrieve Relevant
 Agricultural Knowledge
          ↓
 Multimodal LLM Reasoning
          ↓
 Context-Aware Response
```

---

### LangGraph Agent Workflow

The application uses **LangGraph** to orchestrate the AI processing pipeline.

This makes the system modular and allows individual processing steps to be extended independently.

Example workflow:

```text
WhatsApp Message
       ↓
Message Processing
       ↓
Image / Text Analysis
       ↓
Knowledge Retrieval
       ↓
LLM Reasoning
       ↓
Response Generation
       ↓
WhatsApp Response
```

---

### WhatsApp Cloud API Integration

The project integrates with the **Meta WhatsApp Cloud API**.

It supports:

* Webhook verification
* Incoming text messages
* Incoming images
* Media retrieval
* Message processing
* Automated WhatsApp responses
* Webhook signature validation

---

### Webhook Security

Incoming webhook requests are validated using Meta's:

```text
X-Hub-Signature-256
```

The signature is verified using **HMAC-SHA256** and the application's Meta App Secret.

This prevents unauthorized requests from being processed as legitimate WhatsApp events.

---

### Supabase / Qdrant

Supabase is used as the persistent database layer.

The system can store:

* Farmer/user information
* Conversation history
* Crop-related context
* AI-generated responses
* Session information
* Relevant workflow data
* Qdrant to store vector embeddings for persistence

This enables conversational context and future personalization.

---

### ⚡ FastAPI Backend

The backend is implemented using **FastAPI** and exposes webhook and health endpoints.

Example endpoints:

```text
GET  /webhook/whatsapp
POST /webhook/whatsapp
GET  /health
```

FastAPI provides asynchronous request handling and integrates naturally with the external APIs used by the application.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │      Farmer         │
                         │     WhatsApp        │
                         └──────────┬──────────┘
                                    │
                                    │ Image / Question
                                    ▼
                         ┌─────────────────────┐
                         │ Meta WhatsApp Cloud │
                         │        API          │
                         └──────────┬──────────┘
                                    │
                                    │ Webhook
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │      Backend        │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                ┌────────────────┐    ┌─────────────────┐
                │ Meta Graph API │    │    Supabase     │
                │ Media Retrieval│    │   PostgreSQL    │
                └───────┬────────┘    └─────────────────┘
                        │
                        ▼
                ┌─────────────────────┐
                │    LangGraph        │
                │   AI Workflow       │
                └──────────┬──────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌───────────────┐       ┌─────────────────┐
       │ RAG Retrieval │       │ Multimodal LLM  │
       │ Agricultural  │       │     / Groq      │
       │ Knowledge     │       └────────┬────────┘
       └───────┬───────┘                │
               │                        │
               └────────────┬───────────┘
                            ▼
                  ┌─────────────────────┐
                  │ Response Generation │
                  └──────────┬──────────┘
                             │
                             ▼
                    WhatsApp Response
```

---

# 🛠️ Technology Stack

| Category             | Technology                |
| -------------------- | ------------------------- |
| Programming Language | Python                    |
| Backend              | FastAPI                   |
| AI Orchestration     | LangGraph                 |
| LLM                  | Groq / Vision-capable LLM |
| Generative AI        | Multimodal LLM            |
| Retrieval            | RAG                       |
| Embeddings           | Sentence Transformers     |
| Database             | PostgreSQL / Supabase     |
| Messaging            | Meta WhatsApp Cloud API   |
| HTTP Client          | HTTPX                     |
| Image Processing     | Pillow                    |
| Security             | HMAC-SHA256               |
| Configuration        | python-dotenv             |
| Deployment           | Render                    |
| Version Control      | Git / GitHub              |

---

# 📂 Project Structure

```text
AgroTech-WhatsApp-AI/
│
├── graph/
│   ├── workflow.py
│   ├── state.py
│   └── nodes/
│
├── Rag/
│   ├── db.py
│   ├── retriever.py
│   └── ...
│
├── schemas/
│   └── ...
│
├── main_api.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 🔄 End-to-End Workflow

### 1. Farmer sends an image

The farmer sends a crop image through WhatsApp.

### 2. Meta sends webhook event

Meta WhatsApp Cloud API sends the message event to:

```text
POST /webhook/whatsapp
```

### 3. Webhook authentication

The backend verifies:

```text
X-Hub-Signature-256
```

using HMAC-SHA256.

### 4. Media retrieval

The WhatsApp media ID is extracted from the webhook payload.

The application calls:

```text
GET https://graph.facebook.com/{version}/{media-id}
```

to retrieve the media URL.

### 5. Image processing

The image is downloaded and converted into a model-compatible representation.

### 6. AI workflow

The image and user question are passed into the LangGraph workflow.

### 7. Knowledge retrieval

Relevant agricultural information can be retrieved through the RAG pipeline.

### 8. Multimodal reasoning

The vision-capable LLM analyzes the image and contextual information.

### 9. Response generation

The workflow generates an actionable response.

### 10. WhatsApp response

The response is sent back using:

```text
POST /{phone-number-id}/messages
```

---

# 🔐 Environment Variables

Create a `.env` file locally:

```env
META_ACCESS_TOKEN=your_meta_access_token
META_PHONE_NUMBER_ID=your_phone_number_id
META_VERIFY_TOKEN=your_webhook_verify_token
META_APP_SECRET=your_meta_app_secret

GROQ_API_KEY=your_groq_api_key

SUPABASE_DB_URI=your_supabase_database_uri
```

**Never commit `.env` or API keys to GitHub.**

Add:

```text
.env
```

to `.gitignore`.

---

# ▶️ Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/your-username/AgroTech-WhatsApp-AI.git
cd AgroTech-WhatsApp-AI
```

## 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create:

```text
.env
```

and add the required credentials.

## 5. Start FastAPI

```bash
uvicorn main_api:app --reload --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

---

# 🌐 WhatsApp Webhook Configuration

For local development, expose the FastAPI server using a tunneling service such as ngrok.

Example:

```bash
ngrok http 8000
```

Configure the Meta webhook:

```text
Callback URL:
https://your-domain.com/webhook/whatsapp
```

Verification token:

```text
your META_VERIFY_TOKEN
```

Subscribe to the required WhatsApp message events.

For production, use the deployed Render URL instead of localhost.

---

# 🧪 Testing

### Health check

```http
GET /health
```

Expected:

```json
{
  "status": "ok"
}
```

### Webhook verification

```http
GET /webhook/whatsapp
```

Meta uses:

```text
hub.mode
hub.verify_token
hub.challenge
```

The server returns the challenge when the verification token matches.

---

# 📊 Engineering Highlights

This project demonstrates practical experience with:

* **REST API development**
* **Asynchronous Python**
* **FastAPI**
* **Webhook architecture**
* **Third-party API integration**
* **Meta Graph API**
* **WhatsApp Cloud API**
* **Multimodal AI**
* **Large Language Models**
* **Retrieval-Augmented Generation**
* **LangGraph orchestration**
* **PostgreSQL**
* **Supabase**
* **HMAC authentication**
* **Cloud deployment**
* **Environment-based configuration**
* **Error handling**
* **Background task processing**

---

# 🧠 Key Technical Challenges Solved

### WhatsApp Webhook Verification

Implemented Meta webhook verification using:

```text
hub.mode
hub.verify_token
hub.challenge
```

### Webhook Security

Implemented HMAC-SHA256 validation using:

```text
X-Hub-Signature-256
```

### WhatsApp Media Retrieval

Implemented the two-step Meta Graph API flow:

```text
Media ID
   ↓
Graph API
   ↓
Media URL
   ↓
Image bytes
```

### Multimodal Data Handling

Converted downloaded image bytes into a model-compatible base64 data URI:

```text
bytes
  ↓
Base64
  ↓
data:image/jpeg;base64,...
```

### Stateful AI Processing

Stored farmer conversations in PostgreSQL/Supabase to support future contextual interactions.

### Asynchronous Webhook Processing

Used FastAPI `BackgroundTasks` so that the webhook can acknowledge Meta quickly while AI processing continues in the background.

---

# 🚀 Future Improvements

* [ ] Add crop-specific disease knowledge bases in deep
* [ ] Add voice-message support
* [ ] Add OCR for agricultural labels/documents
* [ ] Add conversation memory
* [ ] Add farmer-specific crop profiles
* [ ] Add analytics dashboard
* [ ] Add LangSmith observability
* [ ] Add automated evaluation for RAG responses
* [ ] Add automated CI/CD
* [ ] Add monitoring and alerting

---

# ⚠️ Disclaimer

AgroTech WhatsApp AI is an AI-assisted agricultural information system and should not replace professional agronomists or agricultural experts.

Disease identification and treatment recommendations should be verified before applying chemicals, pesticides, or other interventions.

---

# 👩‍💻 Developer

**Riya Jangid**

AI/ML & Generative AI Developer

Interested in:

* Generative AI
* LLM Applications
* RAG Systems
* AI Agents
* LangGraph
* Computer Vision
* Machine Learning
* MLOps

📌 Open to **AI/ML Engineer, Generative AI, Data Science, and Software Engineering opportunities**.

---

# ⭐ If You Find This Project Interesting

If you are a recruiter, developer, researcher, or startup founder interested in **Generative AI, multimodal AI, RAG, or AI-powered agricultural solutions**, feel free to connect.

If you find the project useful, consider giving the repository a ⭐.
