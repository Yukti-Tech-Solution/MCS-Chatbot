# Quick Setup Guide

## Step-by-Step Setup Instructions

### 1. Backend Setup

#### A. Create Environment File

Create a file named `.env` in the `backend` folder with the following content:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
SUPABASE_URL=YOUR_SUPABASE_URL_HERE
SUPABASE_KEY=YOUR_SUPABASE_KEY_HERE
```

**Windows PowerShell:**
```powershell
cd backend
@"
GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
SUPABASE_URL=YOUR_SUPABASE_URL_HERE
SUPABASE_KEY=YOUR_SUPABASE_KEY_HERE
"@ | Out-File -FilePath .env -Encoding utf8
```

#### B. Set Up Supabase Database

1. Go to your Supabase project: https://xobptwokoxlwwkyidooc.supabase.co
2. Navigate to **SQL Editor** (left sidebar)
3. Click **New Query**
4. Open `backend/supabase_setup.sql` file and copy all the SQL
5. Paste it into the SQL Editor
6. Click **Run** (or press F5)

This will create:
- `mcs_documents` table
- Vector similarity search function
- Required indexes

#### C. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note:** First-time installation will download the embedding model (~80MB), which may take a few minutes.

#### D. Add PDF Files

1. Place your MCS Act PDF files in the `backend/pdfs` folder
2. The folder should look like:
   ```
   backend/pdfs/
   ├── mcs_act_2023.pdf
   ├── mcs_act_rules.pdf
   └── ...
   ```

#### E. Process PDFs

```bash
python pdf_processor.py
```

This will:
- Extract text from all PDFs
- Create chunks (500 words each)
- Generate embeddings
- Upload to Supabase

Wait for the message: `Successfully processed X PDFs, Y chunks`

#### F. Start Backend Server

```bash
uvicorn main:app --reload
```

Server will run at: **http://localhost:8000**

Test it: Open **http://localhost:8000/docs** in your browser

---

### 2. Frontend Setup

#### A. Install Dependencies

```bash
cd frontend
npm install
```

#### B. Create Environment File (Optional)

If your backend runs on a different port, create `.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

#### C. Start Frontend Server

```bash
npm run dev
```

App will run at: **http://localhost:5173**

---

### 3. Test the Application

1. Open **http://localhost:5173** in your browser
2. You should see the chat interface
3. Try asking: "What are the requirements for forming a cooperative society?"

---

## Troubleshooting

### Backend won't start
- Check that `.env` file exists in `backend` folder
- Verify all API keys are correct
- Make sure port 8000 is not in use

### "Failed to search documents"
- Run `supabase_setup.sql` in Supabase SQL Editor
- Make sure you've processed PDFs with `pdf_processor.py`
- Check Supabase credentials in `.env`

### Frontend can't connect
- Verify backend is running on port 8000
- Check browser console for errors
- Verify `VITE_API_URL` in `.env.local` matches backend URL

### PDF processing fails
- Ensure PDF files are in `backend/pdfs` folder
- Check PDF files are not corrupted
- Verify Supabase connection is working

---

## Next Steps

1. ✅ Backend running on port 8000
2. ✅ Frontend running on port 5173
3. ✅ PDFs processed and uploaded
4. ✅ Database configured
5. 🎉 Start chatting!

---

## Need Help?

- Check `backend/README.md` for detailed backend documentation
- Check main `README.md` for project overview
- Review API docs at http://localhost:8000/docs

