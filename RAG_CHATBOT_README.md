# RAG Chatbot Setup Guide

This guide will help you set up and deploy the RAG-based chatbot for your Docusaurus book.

## 📋 Prerequisites

1. **Google Gemini API Key**
   - Get your free API key from: https://aistudio.google.com/app/apikey
   - Free tier: 1,500 requests/day

2. **Qdrant Cloud Account**
   - Create a free tier cluster at: https://cloud.qdrant.io
   - Free tier: 1GB storage (sufficient for this project)

3. **Node.js & Python**
   - Node.js ≥ 20.0
   - Python ≥ 3.9

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies

**Install Python packages:**
```bash
pip install google-generativeai==0.8.3 qdrant-client==1.11.3 python-dotenv==1.0.1 markdown
```

**Install Node.js packages:**
```bash
npm install
```

### Step 2: Configure Environment Variables

1. Copy the example file:
```bash
cp .env.local.example .env.local
```

2. Edit `.env.local` and fill in your credentials:
```env
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_URL=https://your-cluster-url.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here
```

**How to get Qdrant credentials:**
1. Go to https://cloud.qdrant.io and create a free cluster
2. Once created, go to "Data Access Control" to get your API key
3. The URL will be in the format: `https://xxxxx-xxxxx.qdrant.io:6333`

### Step 3: Index Your Documents

Run the indexing script to process all markdown files and upload embeddings to Qdrant:

```bash
python scripts/index_documents.py
```

**Expected output:**
- ✅ Collection 'docs' created
- ✅ Processed 23 files into ~70 chunks
- ✅ Generated ~70 embeddings
- ✅ Uploaded to Qdrant successfully

**Note:** This step only needs to be run once, or whenever you update your documentation content.

---

## 🧪 Testing Locally

### Test the Backend API

1. Start the development server:
```bash
npm start
```

2. In a separate terminal, start Vercel dev server for API:
```bash
npx vercel dev
```

3. Test the health endpoint:
```bash
curl http://localhost:3000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "qdrant": true,
  "gemini": true
}
```

4. Test the chat endpoint:
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is ROS 2?"}'
```

### Test the Frontend

1. Navigate to http://localhost:3000
2. Click the chat icon in the bottom-right corner
3. Ask a question like "What is ROS 2?"
4. Verify:
   - ✅ Response is generated based on book content
   - ✅ Sources are cited with clickable links
   - ✅ Chat history persists in localStorage
   - ✅ Dark mode works correctly

---

## 🌐 Deployment to Vercel

### Option 1: Deploy via Vercel Dashboard

1. Push your code to GitHub

2. Go to https://vercel.com and import your repository

3. Configure environment variables in Vercel dashboard:
   - `GEMINI_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`

4. Deploy!

Vercel will automatically:
- Build your Docusaurus site
- Deploy Python serverless functions
- Serve everything from a CDN

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Set environment variables
vercel env add GEMINI_API_KEY
vercel env add QDRANT_URL
vercel env add QDRANT_API_KEY

# Deploy
vercel --prod
```

---

## 🔧 Troubleshooting

### Indexing Script Errors

**Error: `GEMINI_API_KEY not found`**
- Solution: Make sure `.env.local` exists and contains your API key

**Error: `ModuleNotFoundError: No module named 'google.generativeai'`**
- Solution: Install Python dependencies: `pip install google-generativeai`

**Error: Qdrant connection failed**
- Solution: Check your `QDRANT_URL` and `QDRANT_API_KEY` are correct
- Verify your Qdrant cluster is running at https://cloud.qdrant.io

### API Endpoint Errors

**Error: 429 Too Many Requests**
- Solution: You've hit the rate limit (10 requests/minute). Wait a minute and try again.

**Error: 500 Internal Server Error**
- Solution: Check the browser console and Vercel logs for details
- Verify environment variables are set correctly

### Frontend Issues

**Chat widget not appearing**
- Solution: Make sure you ran `npm install` to install the `uuid` package
- Check browser console for errors

**Messages not sending**
- Solution: Verify the backend API is running (`http://localhost:3000/api/health`)
- Check CORS errors in browser console

---

## 📊 Usage Monitoring

### Free Tier Limits

**Gemini API (Free Tier):**
- 1,500 requests/day (shared between embeddings and LLM calls)
- ~60 queries/hour

**Qdrant Cloud (Free Tier):**
- 1GB storage (~5MB used for this project)
- Unlimited requests

**Estimated Capacity:**
- ~100 concurrent users
- ~1,000 queries/day

### Monitoring Usage

1. **Gemini API Usage:**
   - Go to https://aistudio.google.com/app/apikey
   - View your usage dashboard

2. **Qdrant Usage:**
   - Go to https://cloud.qdrant.io
   - Check your cluster metrics

---

## 🎯 Testing Checklist

### Functionality Tests

- [ ] Chat icon visible on all pages (bottom-right, 60×60px)
- [ ] Panel opens/closes smoothly with animations
- [ ] Chatbot answers questions accurately based on book content
- [ ] Sources cited with clickable links to doc pages
- [ ] "I don't have enough information" for out-of-scope questions
- [ ] Dark mode works correctly (auto-detects theme)
- [ ] Mobile responsive (full screen on <480px)
- [ ] Error handling for network failures, API timeouts
- [ ] Response time < 5 seconds for typical queries
- [ ] No console errors or warnings
- [ ] Chat history persists in localStorage

### Example Test Queries

**In-Scope (Should Answer):**
- "What is ROS 2?"
- "Explain the Robotic Nervous System"
- "Show me a ROS 2 publisher example"
- "What is NVIDIA Isaac?"
- "Explain Vision-Language-Action models"

**Out-of-Scope (Should Decline):**
- "What's the weather today?"
- "Tell me a joke"
- "Who won the Super Bowl?"

---

## 🔄 Updating Documentation

When you update your markdown files in `docs/`:

1. Re-run the indexing script:
```bash
python scripts/index_documents.py
```

2. Redeploy (Vercel will auto-deploy on git push)

---

## 📚 Architecture Overview

```
User Query
    ↓
ChatWidget (React)
    ↓
POST /api/chat (Python serverless)
    ↓
1. Generate query embedding (Gemini)
2. Search Qdrant for relevant chunks (top 5, score > 0.7)
3. Build context from retrieved chunks
4. Call Gemini LLM with context + query
5. Return response + sources
    ↓
Display in ChatWidget
```

---

## 🛠️ File Structure

```
book/
├── api/                          # Python backend
│   ├── chat.py                   # Chat endpoint
│   ├── health.py                 # Health check
│   ├── requirements.txt          # Python dependencies
│   └── lib/                      # RAG logic
│       ├── gemini_client.py
│       ├── qdrant_client.py
│       └── rag.py
│
├── scripts/                      # Document indexing
│   ├── index_documents.py
│   └── lib/
│       ├── chunker.py
│       └── embeddings.py
│
├── src/                          # Frontend
│   ├── components/
│   │   ├── ChatWidget/           # Chat UI components
│   │   └── ChatContext/          # State management
│   ├── hooks/                    # Custom hooks
│   ├── utils/                    # API client
│   └── theme/
│       └── Root.tsx              # Global integration
│
├── docs/                         # Your markdown content
│   └── **/*.md                   # 23 markdown files
│
├── .env.local                    # Environment variables (not in git)
├── .env.local.example            # Template
└── vercel.json                   # Deployment config
```

---

## 🎨 Customization

### Changing Chat Widget Colors

Edit `src/components/ChatWidget/styles.module.css`:

```css
/* Change primary color */
.chatButton {
  background: #your-color;
}

/* Change user message color */
.userMessage {
  background: #your-color;
}
```

### Changing System Prompt

Edit `api/lib/rag.py`:

```python
SYSTEM_PROMPT = """Your custom instructions here..."""
```

### Changing Chunk Size

Edit `scripts/index_documents.py`:

```python
self.chunker = DocumentChunker(target_chunk_size=500, overlap_size=50)
```

---

## 🆘 Support

If you encounter issues:

1. Check this README's troubleshooting section
2. Review Vercel logs: `vercel logs`
3. Check browser console for frontend errors
4. Verify environment variables are set correctly

---

## ✅ Next Steps

After successful deployment:

1. **Monitor Usage:**
   - Track API usage at https://aistudio.google.com
   - Monitor Qdrant at https://cloud.qdrant.io

2. **Optimize:**
   - Adjust chunk size if needed
   - Fine-tune system prompt
   - Add more suggested questions

3. **Scale:**
   - Upgrade to paid tiers when needed
   - Add caching for frequent queries
   - Implement analytics

---

**Congratulations! Your RAG chatbot is now live! 🎉**
