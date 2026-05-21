# AI Mock Interview Coach

An interactive, full-stack mock interview platform that conducts adaptive technical and behavioral interviews, evaluates both content and delivery, and provides personalized coaching feedback.

Built on a **multi-agent architecture** with five specialized agents that handle different aspects of the interview pipeline — questioning, evaluation, strategy, coaching, and answer rewriting.

---

## Features

### Adaptive Interview Engine
- **5–7 turn adaptive interviews** that adjust difficulty based on candidate performance
- **Intelligent follow-up questions** — never a fixed script; every question reacts to the previous answer
- **Dynamic difficulty scaling** — strong answers trigger harder questions, weak answers trigger probing or topic pivots
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
- **Markdown-formatted feedback** with sections for Strengths, Weaknesses, Communication Style, Key Gaps, What To Practice, and Suggested Questions
- **Aggregate scores** — average score, clarity, depth
- **Answer rewrites** — the 3 weakest answers are rewritten into strong versions, with a diff showing exactly what changed

### Configurable Interview Setup
- Pick your target **role** (any custom role)
- Optional **background** field
- Choose **focus areas** from chips: Technical, Behavioral, HR, System Design, DSA, Group Discussion, Managerial, Case Study

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

## Setup Instructions

### Prerequisites
- **Python 3.10+** — https://www.python.org/downloads/ (check "Add to PATH" during install)
- **Node.js 18+** — https://nodejs.org/
- **Gemini API key** (free) — https://aistudio.google.com/apikey

### 1. Clone and configure

```bash
git clone https://github.com/gunnikaa/AI-mock-interview-coach.git
cd AI-mock-interview-coach

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

## Architecture Overview

### Multi-Agent System

The system is built around five specialized agents, each with a single responsibility. Separating them means each agent can be prompted, tuned, and tested independently.

| Agent | What it does | Input | Output |
|---|---|---|---|
| **Interviewer** | Generates the next question based on the strategist's directive. Adapts tone, difficulty, and topic. | Role, focus, history, strategy directive | Single question (text) |
| **Evaluator** | Scores the candidate's answer on content (correctness, depth, clarity) AND delivery (confidence, fillers, fluency). | Q&A pair | Strict JSON evaluation |
| **Strategist** | Decides what to do next: probe deeper, move on, increase difficulty, or change topic. The "brain" of the adaptive loop. | Full history + last evaluation | Strict JSON directive |
| **Coach** | Reads the entire transcript and writes a personalized coaching report with specific quotes and recommendations. | Full transcript | Markdown report |
| **Rewriter** | Takes the 3 weakest answers and rewrites them into strong versions, applying STAR structure and removing filler. | Weak Q&A pair | JSON with original / improved / what_changed |

### Orchestration — How a Turn Flows

```
   User types/speaks answer
            │
            ▼
   ┌────────────────────┐
   │  POST /answer      │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐    Output: JSON evaluation
   │   EVALUATOR        │    (score, confidence, fillers, ...)
   └────────┬───────────┘
            │  evaluation stored in memory
            ▼
   ┌────────────────────┐    Output: JSON directive
   │   STRATEGIST       │    (probe_deeper / move_on /
   │                    │     increase_difficulty / change_topic)
   └────────┬───────────┘
            │  directive passed to interviewer
            ▼
   ┌────────────────────┐    Output: next question (text)
   │   INTERVIEWER      │
   └────────┬───────────┘
            │
            ▼
   Response sent back to frontend → user sees next question
```

After 6 turns (configurable), `done: true` is returned. The frontend then calls `GET /feedback`, which fires the **Coach** and **Rewriter** agents in sequence to produce the final report.

### Session State

Each interview maintains an in-memory `SessionMemory` keyed by a UUID `session_id`. It stores:
- The interview context (role, background, focus)
- An ordered list of `{question, answer, evaluation}` turns
- Created-at timestamp

When the interview ends, the session is auto-serialized to `transcripts/session_<timestamp>.json` for later review.

### Frontend ↔ Backend

The frontend (Vite dev server on port 5173) **proxies** all API routes (`/start`, `/answer`, `/feedback`, `/session`) to the backend on port 8000. This eliminates CORS issues entirely — from the browser's perspective, everything is same-origin.

---

## Key Design Decisions and Tradeoffs

### 1. Why five separate agents instead of one big prompt?
**Decision:** Split the pipeline into Interviewer / Evaluator / Strategist / Coach / Rewriter.

**Tradeoff:** More LLM calls per turn (3 instead of 1) → higher latency and more rate-limit pressure.

**Why we did it anyway:**
- Each agent has a *very* different job. Asking one prompt to "evaluate AND decide what to ask next AND ask it" produces vague, generic outputs.
- Separation lets us enforce strict JSON output on the evaluator and strategist (machine-readable), while keeping the interviewer's output natural conversational text.
- We can iterate on a single prompt in isolation — improving the Evaluator doesn't risk regressing the Interviewer.

### 2. Why analyze delivery from text instead of audio?
**Decision:** Speech-to-text is handled by the browser's Web Speech API on the frontend. The backend only receives text.

**Tradeoff:** We lose true acoustic signals (pitch, pause length, vocal energy).

**Why:**
- Keeps the backend stateless and language-model-only — no audio processing infra.
- Most delivery problems are detectable from text: filler words ("um", "like", "you know") appear in the transcript, hedging language ("I think maybe", "I'm not sure") reveals confidence, and run-on sentences expose lack of structure.
- Browser speech-to-text is free, fast, and works offline-ish; sending audio to the backend would have meant another paid API (Whisper / Google Speech-to-Text) and 2× the latency.

### 3. Why in-memory sessions instead of a database?
**Decision:** Sessions live in a Python `dict`, not Redis or Postgres.

**Tradeoff:** Sessions are lost on backend restart. Doesn't scale to multiple server instances.

**Why:**
- The product is single-user practice — there's no value in persistence across server restarts.
- Adding a DB adds setup friction for anyone trying the project, with no user-facing benefit.
- Transcripts are still saved to disk as JSON, so the *useful* state survives.

### 4. Strict JSON output for Evaluator and Strategist
**Decision:** Prompts demand JSON, parsed with `json.loads()`, with a safe fallback if parsing fails.

**Tradeoff:** Occasionally the LLM wraps output in markdown code fences or adds a preamble, causing parse failures.

**Why:**
- We need structured data downstream — the Strategist *must* know if the last score was below 5 to choose `probe_deeper`. Free-form prose would require yet another parsing layer.
- We strip code fences with a regex before parsing, and on parse failure we return a neutral default so the interview keeps flowing instead of erroring out.

### 5. Model fallback chain (`gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemini-2.0-flash` → ...)
**Decision:** `utils/llm.py` tries multiple Gemini models in order. On 429 (rate limit) or 404 (model not available in region), it skips to the next.

**Tradeoff:** If the first model is sometimes available, the *quality* across responses can drift slightly between models.

**Why:**
- The free tier of Gemini has per-model daily quotas. Spreading load across models triples effective availability without paying.
- If a newer model is region-locked, the fallback chain degrades gracefully to an older one.

### 6. Why the Rewriter only fixes the *3 weakest* answers, not all
**Decision:** Sort answers by score, take the bottom 3, rewrite those.

**Why:**
- Rewriting all 6 turns means 6 more LLM calls in the `/feedback` step — slow and quota-heavy.
- Coaches in real life focus on the worst moments, not every moment. The strongest answers don't need rewriting.

### 7. Vite proxy instead of CORS headers
**Decision:** All `/start`, `/answer`, `/feedback`, `/session` requests from the browser go to `localhost:5173`, and Vite proxies them to `localhost:8000`.

**Why:**
- `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true` is a silently invalid CORS combination that Chrome blocks. Hitting this caused hours of "Could not connect to server" debugging.
- Same-origin proxying sidesteps CORS entirely. Works on every browser, no config.

### 8. Graceful degradation on agent failure
**Decision:** If the Evaluator or Strategist throws, the turn continues with a neutral default. Only the Interviewer (the user-visible output) is required to succeed.

**Why:**
- Free-tier rate limits will eventually hit mid-interview. Killing the whole session on a transient 429 is the worst UX.
- A degraded turn (no fine evaluation) is still better than a dead session.

---

## Example Transcripts

Three transcripts ship with the project to demonstrate the system's behavior across very different candidates:

### [`transcripts/strong_candidate.md`](transcripts/strong_candidate.md) — Strong Candidate
**Average score: 9.0/10.** Senior backend engineer with concrete examples, quantified results (e.g. "5s → 200ms latency", "$80k/mo saved"), and confident delivery. Demonstrates the system's `increase_difficulty` behavior — the strategist keeps escalating because the candidate keeps clearing the bar.

### [`transcripts/weak_candidate.md`](transcripts/weak_candidate.md) — Weak Candidate
**Average score: 2.3/10.** Vague answers, heavy filler words ("um", "like", "sort of"), deflected ownership ("the senior engineers decided"). Demonstrates `probe_deeper` followed by `change_topic` when probes don't yield better answers. Includes a Rewriter example showing how the weakest answer is transformed into a strong STAR-format response.

### [`transcripts/tricky_candidate.md`](transcripts/tricky_candidate.md) — Tricky / Edge Case
**Average score: 6.3/10** — but the score hides the real story. Self-taught full-stack dev who is **strong on frontend** but cleanly says **"I don't know"** on backend/database questions. Demonstrates:
- The strategist correctly choosing `change_topic` instead of beating a dead horse
- The evaluator distinguishing honest "I don't know" from hedging — penalizing content score but not confidence
- The coach producing feedback that identifies the *pattern* (clear gap in backend), not just the raw number

This is the test case that proves the system isn't just averaging — it's reasoning about the shape of the answers.

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
Returns the full coaching report.

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
├── transcripts/               Sample transcripts + auto-saved sessions
│   ├── strong_candidate.md
│   ├── weak_candidate.md
│   └── tricky_candidate.md
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
