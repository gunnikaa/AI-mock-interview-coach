# AI Mock Interview Coach

An interactive, full-stack mock interview platform that conducts adaptive technical and behavioral interviews, evaluates both content and delivery, and provides personalized coaching feedback.

The system uses a multi-agent architecture with five specialized agents handling different parts of the pipeline: questioning, evaluation, strategy, coaching, and answer rewriting.

---

## Features

### Adaptive Interview Engine
- 5–7 turn adaptive interviews that adjust difficulty based on candidate performance
- Intelligent follow-up questions — no fixed script, every question reacts to the previous answer
- Dynamic difficulty scaling — strong answers trigger harder questions, weak answers trigger probing or topic pivots
- Topic-aware pivots — the system moves on when a topic is exhausted

### Dual Input Modes
- Text input — type your answer like a chat interface
- Speech-to-text via microphone — speak your answers naturally using the browser's Web Speech API, with live transcription as you talk
- Mic button shows a pulsing animation while recording

### Deep Evaluation (Content + Delivery)
Every answer is scored on two axes.

Content:
- Correctness, depth, clarity (1–10 scale each)

Delivery (inferred from the text itself):
- Confidence level: low / medium / high — detected from hedging vs assertive language
- Filler word usage: low / medium / high — counts "um", "uh", "like", "you know" etc.
- Fluency: poor / average / good — based on sentence structure and coherence

### Personalized Coaching Report
- Markdown-formatted feedback with sections for Strengths, Weaknesses, Communication Style, Key Gaps, What To Practice, and Suggested Questions
- Aggregate scores: average score, clarity, depth
- Answer rewrites — the 3 weakest answers are rewritten into strong versions, with a diff showing what changed

### Configurable Interview Setup
- Pick your target role (any custom role)
- Optional background field
- Choose focus areas from chips: Technical, Behavioral, HR, System Design, DSA, Group Discussion, Managerial, Case Study

---

## Tech Stack

Backend:
- Python 3.10+
- FastAPI + Uvicorn
- Google Gemini API (`google-genai` SDK)
- Pydantic v2

Frontend:
- React 19 + TypeScript
- Vite (dev server + build)
- TanStack Router (file-based routing)
- Tailwind CSS 4 + shadcn/ui
- Axios for HTTP
- Web Speech API for microphone input

---

## Setup Instructions

### Prerequisites
- Python 3.10+ — https://www.python.org/downloads/ (check "Add to PATH" during install)
- Node.js 18+ — https://nodejs.org/
- Gemini API key (free) — https://aistudio.google.com/apikey

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

Open two terminal windows.

Terminal 1 — Backend:
```bash
venv\Scripts\activate
python main.py
```
Runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

Terminal 2 — Frontend:
```bash
cd frontend
npm run dev
```
Runs at `http://localhost:5173`.

Open `http://localhost:5173` in your browser and start an interview.

---

## Architecture Overview

### Multi-Agent System

The system is built around five specialized agents, each with a single responsibility. Splitting them this way means each agent can be prompted, tuned, and tested independently.

| Agent | What it does | Input | Output |
|---|---|---|---|
| Interviewer | Generates the next question based on the strategist's directive. Adapts tone, difficulty, and topic. | Role, focus, history, strategy directive | Single question (text) |
| Evaluator | Scores the candidate's answer on content (correctness, depth, clarity) and delivery (confidence, fillers, fluency). | Q&A pair | Strict JSON evaluation |
| Strategist | Decides what to do next: probe deeper, move on, increase difficulty, or change topic. The brain of the adaptive loop. | Full history + last evaluation | Strict JSON directive |
| Coach | Reads the full transcript and writes a personalized coaching report with specific quotes and recommendations. | Full transcript | Markdown report |
| Rewriter | Takes the 3 weakest answers and rewrites them, applying STAR structure and removing filler. | Weak Q&A pair | JSON with original / improved / what_changed |

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

After 6 turns (configurable), `done: true` is returned. The frontend then calls `GET /feedback`, which fires the Coach and Rewriter agents in sequence to produce the final report.

### Session State

Each interview maintains an in-memory `SessionMemory` keyed by a UUID `session_id`. It stores:
- The interview context (role, background, focus)
- An ordered list of `{question, answer, evaluation}` turns
- Created-at timestamp

When the interview ends, the session is auto-serialized to `transcripts/session_<timestamp>.json` for later review.

### Frontend ↔ Backend

The Vite dev server on port 5173 proxies all API routes (`/start`, `/answer`, `/feedback`, `/session`) to the backend on port 8000. This eliminates CORS issues entirely — from the browser's perspective, everything is same-origin.

---

## Key Design Decisions and Tradeoffs

### 1. Five separate agents instead of one big prompt

Splitting the pipeline into Interviewer / Evaluator / Strategist / Coach / Rewriter means more LLM calls per turn (3 instead of 1), so higher latency and more rate-limit pressure.

The reason we did it anyway: each agent has a very different job. Asking one prompt to "evaluate AND decide what to ask next AND ask it" produces vague, generic outputs. Separation also lets us enforce strict JSON output on the Evaluator and Strategist while keeping the Interviewer's output natural conversational text. And we can iterate on one prompt in isolation — improving the Evaluator doesn't risk regressing the Interviewer.

### 2. Analyzing delivery from text, not audio

Speech-to-text is done by the browser's Web Speech API on the frontend. The backend only sees text. The tradeoff is that we lose acoustic signals like pitch, pause length, and vocal energy.

The reason: it keeps the backend stateless and language-model-only, no audio processing infra. And most delivery problems show up in text anyway — filler words ("um", "like", "you know") land in the transcript, hedging ("I think maybe", "I'm not sure") reveals confidence, and run-on sentences expose lack of structure. Browser speech-to-text is also free and fast. Sending audio to the backend would have meant another paid API (Whisper or Google Speech-to-Text) and roughly 2x the latency.

### 3. In-memory sessions instead of a database

Sessions live in a Python dict, not Redis or Postgres. They're lost on backend restart and the system doesn't scale to multiple instances.

The reason: this is a single-user practice tool. There's no value in cross-restart persistence. Adding a DB adds setup friction with zero user-facing benefit. The actually useful state — transcripts — is still saved to disk as JSON.

### 4. Strict JSON output for Evaluator and Strategist

Both prompts demand JSON, parsed with `json.loads()` with a safe fallback if parsing fails. Sometimes the model wraps output in markdown code fences or adds a preamble, which can break parsing.

The reason: we need structured data downstream. The Strategist must know if the last score was below 5 to choose `probe_deeper`. Free-form prose would need another parsing layer. We strip code fences with a regex before parsing, and on parse failure we return a neutral default so the interview keeps flowing instead of erroring out.

### 5. Model fallback chain

`utils/llm.py` tries multiple Gemini models in order: `gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemini-2.0-flash` → `gemini-2.0-flash-lite`. On a 429 (rate limit) or 404 (model not available), it skips to the next one. Response quality can drift slightly between models, which is the tradeoff.

The reason: the free tier of Gemini has per-model daily quotas. Spreading load across models triples effective availability without paying. If a newer model is region-locked, the chain degrades gracefully to an older one.

### 6. Rewriter only fixes the 3 weakest answers

Rewriting all 6 turns means 6 more LLM calls in the `/feedback` step — slow and quota-heavy. Coaches in real life focus on the worst moments, not every moment. The strong answers don't need rewriting.

### 7. Vite proxy instead of CORS headers

All `/start`, `/answer`, `/feedback`, `/session` requests from the browser go to `localhost:5173`, and Vite proxies them to `localhost:8000`.

The reason: `Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true` is a silently invalid CORS combination that Chrome blocks. Same-origin proxying sidesteps CORS entirely, works on every browser, no config needed.

### 8. Graceful degradation on agent failure

If the Evaluator or Strategist throws, the turn continues with a neutral default. Only the Interviewer (the user-visible output) is required to succeed.

The reason: free-tier rate limits will hit mid-interview eventually. Killing the whole session on a transient 429 is the worst possible UX. A degraded turn with a generic evaluation is still better than a dead session.

---

## Example Transcripts

Three transcripts demonstrate the system's behavior across very different candidates.

---

### Transcript 1 — Strong Candidate

Role: Senior Software Engineer
Background: 5 years backend engineering, Python + distributed systems
Focus: System design, leadership, problem-solving

What this demonstrates: the strategist's `increase_difficulty` behavior — the candidate keeps clearing the bar so questions keep escalating.

#### Turn 1

Interviewer: Walk me through a complex technical system you've designed from scratch — what were the key decisions you made and why?

Candidate: Sure. About two years ago I led the design of our real-time notification service. We were sending emails, push notifications, and SMS to about 2 million users per day, and the existing monolith was causing 5-second delays. I made three key decisions: first, I decoupled notification dispatch into its own microservice using a message queue — we chose RabbitMQ because our team already had operational expertise with it and our throughput didn't require Kafka's complexity. Second, I introduced channel-specific workers that could scale independently, since SMS was the bottleneck, not email. Third, I added a dead-letter queue with exponential backoff retry logic to handle transient failures. The result was average dispatch latency dropping from 5 seconds to 200ms, and we got to 99.97% delivery reliability within the first month.

Evaluation: Score 9/10 | Confidence: high | Fluency: good | Depth: 9/10

#### Turn 2

Interviewer: You mentioned choosing RabbitMQ over Kafka — in what scenario would you have chosen Kafka instead?

Candidate: Good distinction. Kafka would have been the right call if we needed event sourcing or replay capability — for instance, if downstream teams needed to consume the same notification events for analytics or audit trails. Kafka's log retention means you can replay events from any point, which is powerful for compliance use cases. Also, if we were looking at throughput above roughly 100k messages per second sustained, Kafka's partitioned architecture handles that more gracefully than RabbitMQ's queue model. For our case, we were at about 25k messages per second peak, and we needed simple point-to-point dispatch, so RabbitMQ was the right tradeoff — lower operational overhead, easier local dev setup, and sufficient scale.

Evaluation: Score 9/10 | Confidence: high | Fluency: good | Depth: 9/10

#### Turn 3

Interviewer: Tell me about a time you had to push back on a decision from product or leadership that you thought was technically wrong.

Candidate: Yes — this happened about a year ago. The VP of Product wanted us to build a new feature that would run a full ML inference call on every page load to personalize content. I calculated that at our traffic levels — about 500 requests per second — this would add roughly $80k per month in GPU costs and 400ms to our P99 latency. I documented both the cost projection and the latency impact in a one-pager, proposed an alternative: pre-computing personalization scores nightly and serving them from Redis. I brought this to the VP directly, showed the numbers, and framed it as "here's how we get 80% of the personalization value at 5% of the cost." She agreed to the alternative. The nightly batch job shipped in two weeks, cost under $3k per month, and the latency impact was under 5ms.

Evaluation: Score 9/10 | Confidence: high | Fluency: good | Depth: 8/10

Final Average: 9.0/10

Coach excerpt: Strong candidate who demonstrates deep technical knowledge with concrete, quantified examples throughout. Every answer includes a specific situation, a measurable result, and a clear thought process. Suggested next questions to push further: "How would you handle a zero-downtime migration on a 500M-row table?" and "Describe a system you'd design differently today."

---

### Transcript 2 — Weak Candidate

Role: Senior Software Engineer
Background: 3 years experience, mostly front-end
Focus: System design, backend, problem-solving

What this demonstrates: the strategist switching to `change_topic` when `probe_deeper` doesn't yield better answers, plus the Rewriter agent transforming a weak answer into a strong one.

#### Turn 1

Interviewer: Walk me through a complex technical system you've designed from scratch — what were the key decisions you made and why?

Candidate: Um, so like, I've worked on some pretty complex things I think. We built a, um, like a dashboard for our company that showed analytics. I sort of helped with the backend? Basically we used React on the front and I think we used Node.js on the back, and like it was pretty complex because there was a lot of data. I don't really remember the specific decisions we made but I know it worked well in the end.

Evaluation: Score 3/10 | Confidence: low | Fluency: poor | Filler words: high | Depth: 2/10

#### Turn 2

Interviewer: You mentioned working on the backend — can you walk me through a specific technical decision you made there, even a small one?

Candidate: Uh, yeah so I think like, we had to decide between, um, different databases? I'm not sure exactly which ones we looked at but I think we went with Postgres because someone on the team said it was good. I didn't really make that decision myself, it was more the senior engineers. I was mostly doing the frontend stuff to be honest, like I said I sort of helped with backend but it was more the other people.

Evaluation: Score 2/10 | Confidence: low | Fluency: poor | Filler words: high | Depth: 1/10
Strategist decision: `change_topic` — second weak answer in a row, time to pivot.

#### Turn 3

Interviewer: Let's switch gears. Tell me about a time you had to deal with a difficult team situation or conflict.

Candidate: Yeah so, um, like we had a disagreement once with a coworker about, like, how to structure the code. I don't really remember the details too well. I think it worked out fine in the end. I'm not really sure how to explain it. Like, you know, these things happen in teams and you just kind of figure it out.

Evaluation: Score 2/10 | Confidence: low | Fluency: poor | Depth: 1/10

Final Average: 2.3/10

#### Rewriter Output (Turn 1)

Original: "Um, so like, I've worked on some pretty complex things I think. We built a, um, like a dashboard..."

Improved: "I led the backend development for an internal analytics dashboard that aggregated data from three microservices into a single view used by our operations team. The most complex decision I made was how to handle data freshness — we needed near-realtime updates but couldn't afford to poll every second at scale. I implemented a WebSocket layer using Socket.IO that pushed updates only when the underlying data changed, which reduced unnecessary server load by about 60% compared to our initial polling approach."

What changed:
- Removed 12 filler words and phrases ("um", "like", "sort of", "I think", "basically")
- Replaced "I sort of helped" with "I led" to establish clear ownership
- Added STAR structure: Situation (analytics dashboard), Task (backend development), Action (WebSocket implementation), Result (60% load reduction)
- Replaced vague "it was complex" with a specific technical problem and solution

Coach excerpt: The candidate consistently deflected ownership ("someone else decided", "I mostly did frontend") and provided answers with no concrete examples, metrics, or technical depth. Top three practice items: (1) STAR method on every behavioral answer, (2) record yourself answering and listen back to count filler words, (3) prepare 5 ownership stories where you made the decision with measurable impact.

---

### Transcript 3 — Tricky / Edge Case Candidate

Role: Full-Stack Developer
Background: Self-taught, 1 year freelance experience
Focus: Technical, Behavioral

Why this is the tricky case: mixed signals. The candidate is confident and articulate on frontend topics, but immediately admits "I don't know" on database/backend questions. This forces the strategist to pivot topics rather than keep probing dead ends, and tests the evaluator's ability to score honesty fairly.

#### Turn 1

Interviewer: Walk me through how you'd structure a React component for a complex form with validation.

Candidate: Sure. For a complex form, I'd reach for React Hook Form combined with Zod for schema validation. The pattern I follow is: define the schema first with Zod, then pass it to React Hook Form via the zodResolver. Each field uses register or Controller depending on whether it's a native input or a custom component. For validation feedback, I display errors inline below each field using the formState.errors object. I'd also debounce any async validation, like a username availability check, to avoid hammering the server on every keystroke.

Evaluation: Score 8/10 | Confidence: high | Fluency: good | Depth: 8/10 | Topic: frontend

#### Turn 2

Interviewer: Good. Now imagine that form needs to save to a Postgres database — how would you handle the transaction if you're inserting into three related tables?

Candidate: Honestly, I don't really know much about transactions. I've only used Postgres through Supabase, and I just call the insert function from their client. I'm not sure how the transaction part works under the hood.

Evaluation: Score 2/10 | Confidence: low | Fluency: average | Depth: 1/10 | Topic: database
Strategist decision: `change_topic` — clear gap, no point probing deeper.

#### Turn 3

Interviewer: Got it. Let's switch gears — tell me about a time you had to debug a tricky performance issue in your code.

Candidate: Yeah, this happened on a freelance project last month. I built a dashboard that loaded a list of about 5000 items and the page was freezing for 3-4 seconds every time you scrolled. I used Chrome DevTools to profile it and saw the bottleneck was that every item was re-rendering on every scroll event because of an unstable callback prop. I wrapped the callback in useCallback and the parent component's filter object in useMemo, and the freeze went away completely. After that I also added react-window for virtualization since 5000 items is still a lot to keep in the DOM.

Evaluation: Score 9/10 | Confidence: high | Fluency: good | Depth: 9/10 | Topic: performance debugging
Strategist decision: `increase_difficulty` — candidate is strong here.

#### Turn 4

Interviewer: Impressive — sounds like you really know the React rendering model. Now imagine the same dashboard, but the slowness is on the initial server response, not the client. How would you diagnose it?

Candidate: Hmm, I honestly haven't done much backend work. I'd probably just look at the network tab to see how long the API call takes. Beyond that I'd ask a backend dev for help. I'm being honest — that's not really my area.

Evaluation: Score 3/10 | Confidence: medium (honest, not hedging) | Depth: 2/10 | Topic: backend performance

#### Turn 5

Interviewer: Fair enough. Tell me about how you handle disagreements with clients on technical decisions.

Candidate: I had one a few months ago where a client wanted me to build their app in a no-code tool, but their requirements included real-time collaboration which no-code platforms weren't great at. I put together a short doc comparing three approaches: pure no-code, no-code with custom code, and a custom React app. For each I listed effort, monthly cost, and the limitations. I scheduled a 30-minute call and walked them through it. They picked the custom React option in the end because the cost difference over a year was smaller than they expected. The key for me was not arguing in the moment — I went away, structured the tradeoffs, and let them make the call with full information.

Evaluation: Score 8/10 | Confidence: high | Fluency: good | Depth: 7/10 | Topic: communication

#### Turn 6

Interviewer: Last one — what's a tech skill you know you need to learn next, and how would you go about learning it?

Candidate: Yeah, it's exactly what we've been talking about — backend and databases. I've been getting by with Supabase but I can feel that I'm hitting the ceiling of what I can build without understanding what's happening on the server side. My plan is to build one full project end-to-end with Node + Postgres + raw SQL, no ORMs. I learn best by building, not by tutorials. I've blocked out two evenings a week for the next two months for it.

Evaluation: Score 8/10 | Confidence: high | Fluency: good | Depth: 7/10 | Topic: self-awareness

Final Average: 6.3/10 — but the score hides the real story. The candidate was strong on 4 of 6 turns and intentionally weak on the 2 backend questions, which they openly admitted.

Coach excerpt: Two rare and valuable qualities here — deep, specific frontend expertise (Turn 1, Turn 3) and the self-awareness to flag gaps clearly instead of bluffing (Turn 2, Turn 4). The debugging story in Turn 3 is exceptionally well-told: symptom, diagnostic tool, root cause, fix, and the follow-up improvement. Clear gap: backend and database fundamentals. Recommendation: add a constraint to the planned Node + Postgres project — implement at least one multi-table transaction with proper rollback handling.

What this transcript proves about the system:
- The strategist correctly chose `change_topic` after Turn 2 instead of probing harder on a known gap
- The evaluator distinguished honest "I don't know" from hedging, penalizing content score but not confidence
- The coach feedback identifies the pattern (clear gap in backend), not just the raw average
- This is the test case that proves the system isn't just averaging — it's reasoning about the shape of the answers

---

## API Reference

### POST /start
Begin a new session.

Request:
```json
{
  "role": "Software Engineer",
  "background": "2nd year B.Tech AIML student",
  "focus": "Technical, Behavioral"
}
```

Response:
```json
{
  "session_id": "uuid",
  "question": "Tell me about yourself...",
  "turn": 1
}
```

### POST /answer
Submit an answer (typed or speech-to-text).

Request:
```json
{ "session_id": "uuid", "answer": "..." }
```

Response:
```json
{ "question": "follow-up question", "turn": 2, "done": false }
```

When `done: true`, the interview is complete — call `/feedback`.

### GET /feedback?session_id=<uuid>
Returns the full coaching report.

Response:
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

### DELETE /session/{session_id}
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
