# Setup Checklist

Use this checklist to verify everything is set up correctly.

## ✅ Pre-Setup Verification

- [ ] Python 3.10+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] All project files created in correct directories
- [ ] API keys available (Groq, Gemini, Supabase)

## ✅ Backend Setup

- [ ] `.env` file created in `backend/` folder with all API keys
- [ ] Supabase database table created (run `supabase_setup.sql`)
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] PDF files placed in `backend/pdfs/` folder
- [ ] PDFs processed successfully (`python pdf_processor.py`)
- [ ] Backend server starts without errors (`uvicorn main:app --reload`)
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health check works: http://localhost:8000/api/health

## ✅ Frontend Setup

- [ ] Node dependencies installed (`npm install`)
- [ ] `.env.local` created (optional, if different backend URL)
- [ ] Frontend server starts without errors (`npm run dev`)
- [ ] App accessible at http://localhost:5173
- [ ] No console errors in browser

## ✅ Integration Testing

- [ ] Can send a message in the chat interface
- [ ] Backend receives and processes the question
- [ ] Response is generated and displayed
- [ ] Sources are shown (if available)
- [ ] Error messages display correctly (if API fails)
- [ ] Loading states work correctly

## ✅ Functionality Testing

- [ ] Ask: "What are the requirements for forming a cooperative society?"
- [ ] Verify response is relevant and cites sources
- [ ] Test with multiple questions
- [ ] Verify auto-scroll works
- [ ] Test Enter key (send) and Shift+Enter (new line)
- [ ] Verify error handling when backend is down

## 🎉 Ready for Use!

Once all items are checked, your chatbot is ready to use!

