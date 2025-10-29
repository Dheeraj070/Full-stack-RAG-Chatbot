# 🤖 Engineering Chatbot

**An AI-powered chatbot for engineering students with PDF analysis capabilities**

---

## 📖 What is This?

This is a full-stack web application that lets engineering students:

- Chat with an AI assistant about engineering topics
- Upload PDF documents (textbooks, papers, notes)
- Ask questions about uploaded PDFs and get AI-generated answers
- Manage chat sessions and conversation history

The application uses **RAG (Retrieval-Augmented Generation)** to provide accurate,
context-aware responses based on your uploaded documents.

---

## 🎯 How It Works

1. User uploads a PDF document.
2. System extracts text and splits it into chunks.
3. Embeddings are generated for each chunk.
4. Vectors are stored in FAISS (fast search) with MongoDB as a backup.
5. User asks a question; system finds most relevant chunks via vector similarity.
6. Relevant context + question are sent to Google Gemini AI for answer generation.

---

## 🛠️ Tech Stack

### Frontend

- React + TypeScript — UI framework
- Tailwind CSS — Styling
- Firebase Auth — Authentication (Email + Google Sign-In)
- Axios — API requests

### Backend

- Flask — Python web framework
- MongoDB — Database (users, chats, sessions, PDFs)
- FAISS — Fast vector similarity search
- Sentence-Transformers — Generate embeddings
- Google Gemini AI — Generate responses
- PyPDF2 — Extract text from PDFs
- Firebase Admin — Verify authentication

### Key Technologies

- RAG: Retrieval-Augmented Generation
- Vector Embeddings: 384-dimensional vectors for semantic search
- JWT: Secure session management

---

## 📁 Directory Structure

```
engineering-chatbot/
├── backend/                # Flask REST API
│   ├── app/
│   │   ├── models/         # Database models (User, Chat, PDF, etc.)
│   │   ├── routes/         # API endpoints (auth, chat, admin)
│   │   ├── utils/          # Utilities (FAISS, PDF processing, AI)
│   │   └── __init__.py     # App initialization
│   ├── uploads/            # Uploaded PDF files
│   ├── faiss_data/         # FAISS vector indices
│   ├── requirements.txt    # Python dependencies
│   ├── run.py              # Start backend server
│   └── .env                # Environment variables (create this)
├── frontend/               # React TypeScript App
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Pages (Login, StudentChat, AdminDashboard)
│   │   ├── contexts/       # React contexts (Auth)
│   │   ├── services/       # API client
│   │   └── config/
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite configuration
└── README.md               # This file
```

---

## 🚀 How to Run

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (or MongoDB Atlas)

### 1) Setup Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (you can copy from `.env.example`) and set:

- MONGO_URI=mongodb://localhost:27017/engineering_chatbot
- GEMINI_API_KEY=your-gemini-api-key-here
- SECRET_KEY=your-secret-key
- JWT_SECRET_KEY=your-jwt-secret
- FIREBASE_CREDENTIALS_PATH=firebase-credentials.json

Start the backend:

```bash
python run.py
# Backend runs at: http://localhost:5000
```

### 2) Setup Frontend

Open a new terminal and run:

```bash
cd frontend
npm install
```

Copy `frontend/.env.example` to `.env` and set the Firebase and API variables, e.g.:

- VITE_API_BASE_URL=http://localhost:5000/api
- VITE_FIREBASE_API_KEY=your-firebase-api-key
- VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
- VITE_FIREBASE_PROJECT_ID=your-project-id
- VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
- VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
- VITE_FIREBASE_APP_ID=1:123456789:web:abc123

Build CSS and start dev server:

```bash
npm run build:css
npm run dev
# Frontend runs at: http://localhost:3000
```

### 3) Use the App

1. Open http://localhost:3000 in your browser.
2. Register a new account (role: Student).
3. Login, upload a PDF, and start chatting.

---

## 🎯 Features

For Students

- Upload PDF documents (max 16MB)
- Chat directly with AI about engineering topics
- Ask questions about uploaded PDFs
- Create multiple chat sessions
- View chat history
- Manage uploaded files

For Admins

- Manage users and accounts
- Monitor chat sessions and uploaded files
- View system statistics and manage FAISS vector store

---

## 🔑 Concepts

What is RAG?

Retrieval-Augmented Generation combines retrieval (finding relevant document fragments)
with generation (AI producing an answer) to produce factual, grounded responses.

What is FAISS?

FAISS (Facebook AI Similarity Search) is a fast library for vector similarity
search used to find relevant embeddings quickly.

What are Vector Embeddings?

Text is converted to numerical vectors (e.g., 384 dimensions). Similar text → similar
vectors, which helps find related content.

---

## 🐛 Troubleshooting

- Backend won't start: ensure MongoDB is running and `.env` is configured.
- Frontend won't start: run `npm install` and ensure backend is running.
- Can't login: verify Firebase config and `firebase-credentials.json` in `backend/`.
- PDF upload fails: check file size (max 16MB) and file validity.

---

## 📊 Performance (estimates)

- Vector Search: < 5ms for ~10k vectors
- PDF Processing: ~10–30s (depends on size)
- Chat Response: ~1–4s

---

## 🚢 Deployment

See `DEPLOYMENT.md` for production deployment notes. Suggested free hosting:

- Backend: Railway or Render
- Frontend: Vercel or Netlify
- Database: MongoDB Atlas

---

## 📝 Environment Variables (summary)

Backend `.env` example:

```text
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key
MONGO_URI=mongodb://localhost:27017/engineering_chatbot
GEMINI_API_KEY=your-gemini-key
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
CORS_ORIGINS=http://localhost:3000
```

Frontend `.env` example:

```text
VITE_API_BASE_URL=http://localhost:5000/api
VITE_FIREBASE_API_KEY=your-key
VITE_FIREBASE_AUTH_DOMAIN=your-domain
VITE_FIREBASE_PROJECT_ID=your-id
VITE_FIREBASE_STORAGE_BUCKET=your-bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

---

## 🤝 Contributing

Contributions welcome: report bugs, suggest features, or submit pull requests.

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Dheeraj070

Last Updated: 2025-10-29 11:34:54 UTC

---

## 🎉 Quick Start

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# or: source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python run.py

# Frontend (new terminal)
cd frontend
npm install
npm run build:css
npm run dev
```