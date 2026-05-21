# AI Mock Interview Coach

An interactive, full-stack mock interview platform that conducts adaptive technical and behavioral interviews, evaluates both content and delivery, and provides personalized coaching feedback.

Built on a **multi-agent architecture** with five specialized agents that handle different aspects of the interview pipeline : questioning, evaluation, strategy, coaching, and answer rewriting.

---

## Features

### Adaptive Interview Engine
- **5–7 turn adaptive interviews** that adjust difficulty based on candidate performance
- **Intelligent follow-up questions** — never a fixed script; every question reacts to the previous answer
- **Dynamic difficulty scaling** — strong answers trigger harder questions, weak answers trigger probing
- **Topic-aware pivots** — system automatically moves on when a topic is exhausted

### Dual Input Modes
- **Text input** — type your answer like a chat interface
- **Speech-to-text via microphone** — speak your answers naturally using the browser's Web Speech API; transcription happens live as you talk
- Mic button shows a pulsing animation while recording

### Deep Evaluation (Content + Delivery)
Every answer is scored on:
- **Content**: correctness, depth, clarity (1–10 scale)
- **Delivery (inferred from text)**:
  - Confidence level (low / medium / high) — detected from hedging vs. assertive language
  - Filler word usage (low / medium / high) — counts "um", "uh", "like", "you know" etc.
  - Fluency (poor / average / good) — based on sentence structure and coherence

### Personalized Coaching Report
At the end of the interview you get:
- **Markdown-formatted feedback** with sections for Strengths, Weaknesses, Communication Style, Key Gaps, What To Practice, and Suggested Questions
- **Aggregate scores** — average score, clarity, depth
- **Answer rewrites** — the 3 weakest answers are rewritten into strong versions, with a diff showing exactly what changed

### Configurable Interview Setup
- Pick your target **role** (any custom role)
- Optional **background** field
- Choose **focus areas** from chips: Technical, Behavioral, HR, System Design, DSA, Group Discussion, Managerial, Case Study

### Production-Ready Engineering
- Clean separation: backend (FastAPI) ↔ frontend (React + Vite)
- Session-based state, per-user isolated
- Auto-saved JSON transcripts of every session
- Graceful degradation if any single agent fails
- Automatic model fallback if Gemini quotas are hit

---

## Tech Stack

**Backend**
- Python 3.10+
- FastAPI + Uvicorn
- Google Gemini API (`google-genai` SDK)
- Pydantic v2

**Frontend**
- React 19 + TypeScript
- Vite (dev server + build)
- TanStack Router (file-based routing)
- Tailwind CSS 4 + shadcn/ui
- Axios for HTTP
- Web Speech API for microphone input

---

## Architecture

### Multi-Agent System

Five specialized agents, each handling a single responsibility:

| Agent | Input | Output | Purpose |
|---|---|---|---|
| **Interviewer** | Role + strategist directive | Next question | Adaptive question generation |
| **Evaluator** | Q&A pair | Strict JSON evaluation | Scores content + delivery |
| **Strategist** | Full history + last eval | Strict JSON directive | Decides next interview move |
| **Coach** | Full transcript | Markdown report | End-of-session feedback |
| **Rewriter** | Weak Q&A pairs | JSON with rewritten answer | Improves weakest responses |

### Request Flow

```
POST /start    → opening question
POST /answer   → Evaluator → Strategist → Interviewer → next question  (×5–6 turns)
POST /answer   → done: true (interview complete)
GET  /feedback → Coach + Rewriter → full feedback report
```

---

## Project Structure

```
ai-mock-interview/
├── main.py                    FastAPI entry point
├── requirements.txt           Python dependencies
├── .env.example               Environment variable template
│
├── api/
│   └── routes.py              All API endpoints + orchestration
│
├── agents/
│   ├── interviewer.py         Adaptive question generation
│   ├── evaluator.py           Content + delivery evaluation
│   ├── strategist.py          Interview flow decisions
│   ├── coach.py               End-of-session feedback
│   └── rewriter.py            Answer improvement
│
├── prompts/                   Prompt templates for each agent
│   ├── interviewer.txt
│   ├── evaluator.txt
│   ├── strategist.txt
│   ├── coach.txt
│   └── rewriter.txt
│
├── utils/
│   ├── llm.py                 Gemini client with model fallback
│   ├── memory.py              Session state management
│   └── prompt_loader.py       Loads prompt files
│
├── models/
│   └── schemas.py             Pydantic request/response models
│
├── transcripts/               Auto-saved JSON session logs
│   ├── strong_candidate.md    Sample transcript
│   └── weak_candidate.md      Sample transcript
│
└── frontend/                  React + Vite frontend
    ├── src/
    │   ├── main.tsx
    │   ├── router.tsx
    │   ├── routes/            File-based routes
    │   ├── components/
    │   │   ├── interview/     Setup, Interview, Feedback screens
    │   │   └── ui/            shadcn/ui components
    │   └── lib/
    │       └── api.ts         Axios client
    ├── index.html
    ├── package.json
    └── vite.config.ts         Dev proxy → backend
```

---

## Setup Instructions

### Prerequisites
- **Python 3.10+** — https://www.python.org/downloads/ (check "Add to PATH" during install)
- **Node.js 18+** — https://nodejs.org/
- **Gemini API key** (free) — https://aistudio.google.com/apikey

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd ai-mock-interview

# Create your .env file from the template
copy .env.example .env       # Windows
# cp .env.example .env       # macOS / Linux
```

Open `.env` and paste your Gemini API key:
```
GEMINI_API_KEY=your_actual_key_here
```

### 2. Backend setup

```bash
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd frontend
npm install
cd ..
```

### 4. Run both servers

Open **two terminal windows**.

**Terminal 1 — Backend:**
```bash
venv\Scripts\activate
python main.py
```
Runs at `http://localhost:8000` — API docs at `http://localhost:8000/docs`

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```
Runs at `http://localhost:5173`

Open **http://localhost:5173** in your browser and start an interview.

---

## API Reference

### `POST /start`
Begin a new session.

**Request:**
```json
{
  "role": "Software Engineer",
  "background": "2nd year B.Tech AIML student",
  "focus": "Technical, Behavioral"
}
```
**Response:**
```json
{
  "session_id": "uuid",
  "question": "Tell me about yourself...",
  "turn": 1
}
```

### `POST /answer`
Submit an answer (typed or speech-to-text).

**Request:**
```json
{ "session_id": "uuid", "answer": "..." }
```
**Response:**
```json
{ "question": "follow-up question", "turn": 2, "done": false }
```
When `done: true`, the interview is complete — call `/feedback`.

### `GET /feedback?session_id=<uuid>`
Returns coaching report.

**Response:**
```json
{
  "feedback_markdown": "## Strengths\n...",
  "rewritten_answers": [
    { "original": "...", "improved": "...", "what_changed": ["..."] }
  ],
  "total_turns": 6,
  "average_score": 7.3
}
```

### `DELETE /session/{session_id}`
Cleans up a session.

---

## Configuration

### Adjusting interview length
Edit `api/routes.py`:
```python
MAX_TURNS = 6  # Change to 5, 7, etc.
```

### Model fallback chain
Edit `utils/llm.py` — the `_MODELS` list tries each Gemini model in order. If the first hits a rate limit, it falls back to the next automatically.

### Backend port
Edit `main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### Frontend proxy
The Vite dev server proxies `/start`, `/answer`, `/feedback`, `/session` to `http://127.0.0.1:8000`. If you change the backend port, also update `frontend/vite.config.ts`.

---

## Sample Transcripts

Two example transcripts are included to demonstrate the system's range:

- **`transcripts/strong_candidate.md`** — High-scoring candidate (9.0/10 average) with concrete examples, confident delivery, deep technical answers
- **`transcripts/weak_candidate.md`** — Low-scoring candidate (2.3/10 average) with filler words, deflected ownership, vague answers — includes a rewrite example showing the improvement

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `GEMINI_API_KEY is not set` | Copy `.env.example` → `.env` and paste your key |
| `429 RESOURCE_EXHAUSTED` | Free tier daily quota hit — wait for reset (midnight US Pacific) or use a different Google account |
| `Could not connect to interview server` | Backend isn't running, or you're on the wrong port |
| Mic button does nothing | Use Chrome/Edge — Web Speech API isn't supported in Firefox |
| Frontend `npm install` fails | Make sure Node.js 18+ is installed (`node -v`) |

---

## License

MIT
