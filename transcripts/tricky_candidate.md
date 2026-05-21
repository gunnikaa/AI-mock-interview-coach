# Sample Transcript — Tricky / Edge Case Candidate

**Role:** Full-Stack Developer  
**Background:** Self-taught, 1 year freelance experience  
**Focus:** Technical, Behavioral

**Why this is a tricky case:** Mixed signals — confident and articulate on frontend topics, but immediately admits "I don't know" on database/backend questions. Forces the strategist to pivot topics rather than keep probing dead ends, and tests the evaluator's ability to score honesty fairly.

---

## Turn 1

**Interviewer:** Walk me through how you'd structure a React component for a complex form with validation.

**Candidate:** Sure. For a complex form, I'd reach for React Hook Form combined with Zod for schema validation. The pattern I follow is: define the schema first with Zod, then pass it to React Hook Form via the zodResolver. Each field uses register or Controller depending on whether it's a native input or a custom component. For validation feedback, I display errors inline below each field using the formState.errors object. I'd also debounce any async validation, like a username availability check, to avoid hammering the server on every keystroke.

**Evaluation:** Score 8/10 | Confidence: high | Fluency: good | Depth: 8/10 | Topic: frontend

---

## Turn 2

**Interviewer:** Good. Now imagine that form needs to save to a Postgres database — how would you handle the transaction if you're inserting into three related tables?

**Candidate:** Honestly, I don't really know much about transactions. I've only used Postgres through Supabase, and I just call the insert function from their client. I'm not sure how the transaction part works under the hood.

**Evaluation:** Score 2/10 | Confidence: low | Fluency: average | Depth: 1/10 | Topic: database  
**Strategist decision:** `change_topic` — clear gap, no point probing deeper

---

## Turn 3

**Interviewer:** Got it. Let's switch gears — tell me about a time you had to debug a tricky performance issue in your code.

**Candidate:** Yeah, this happened on a freelance project last month. I built a dashboard that loaded a list of about 5000 items and the page was freezing for 3-4 seconds every time you scrolled. I used Chrome DevTools to profile it and saw the bottleneck was that every item was re-rendering on every scroll event because of an unstable callback prop. I wrapped the callback in useCallback and the parent component's filter object in useMemo, and the freeze went away completely. After that I also added react-window for virtualization since 5000 items is still a lot to keep in the DOM.

**Evaluation:** Score 9/10 | Confidence: high | Fluency: good | Depth: 9/10 | Topic: performance debugging  
**Strategist decision:** `increase_difficulty` — candidate is strong here

---

## Turn 4

**Interviewer:** Impressive — sounds like you really know the React rendering model. Now imagine the same dashboard, but the slowness is on the *initial* server response, not the client. How would you diagnose it?

**Candidate:** Hmm, I honestly haven't done much backend work. I'd probably just look at the network tab to see how long the API call takes. Beyond that I'd ask a backend dev for help. I'm being honest — that's not really my area.

**Evaluation:** Score 3/10 | Confidence: medium (honest, not hedging) | Depth: 2/10 | Topic: backend performance  
**Strategist decision:** `change_topic` — second backend question, second admission

---

## Turn 5

**Interviewer:** Fair enough. Tell me about how you handle disagreements with clients on technical decisions.

**Candidate:** I had one a few months ago where a client wanted me to build their app in a no-code tool, but their requirements included real-time collaboration which no-code platforms weren't great at. I put together a short doc comparing three approaches: pure no-code, no-code with custom code, and a custom React app. For each I listed effort, monthly cost, and the limitations. I scheduled a 30-minute call and walked them through it. They picked the custom React option in the end because the cost difference over a year was smaller than they expected. The key for me was not arguing in the moment — I went away, structured the tradeoffs, and let them make the call with full information.

**Evaluation:** Score 8/10 | Confidence: high | Fluency: good | Depth: 7/10 | Topic: communication

---

## Turn 6

**Interviewer:** Last one — what's a tech skill you know you need to learn next, and how would you go about learning it?

**Candidate:** Yeah, it's exactly what we've been talking about — backend and databases. I've been getting by with Supabase but I can feel that I'm hitting the ceiling of what I can build without understanding what's happening on the server side. My plan is to build one full project end-to-end with Node + Postgres + raw SQL, no ORMs. I learn best by building, not by tutorials. I've blocked out two evenings a week for the next two months for it.

**Evaluation:** Score 8/10 | Confidence: high | Fluency: good | Depth: 7/10 | Topic: self-awareness  
**Interview complete.**

---

## Final Feedback (excerpt)

**Average Score:** 6.3/10 — but the scoring hides the real story: strong on 4/6 turns, intentionally weak on the 2 backend questions which the candidate openly admitted.

## Strengths
The candidate shows two qualities that are rare and valuable: deep, specific frontend expertise (Turn 1, Turn 3) and the self-awareness to flag gaps clearly instead of bluffing (Turn 2, Turn 4). The debugging story in Turn 3 is exceptionally well-told — it includes the symptom, the diagnostic tool used, the root cause, the fix, and the follow-up improvement...

## Weaknesses
Backend and database fundamentals are a clear gap. This is the kind of gap that will block more senior roles regardless of how strong the frontend skills are...

## What To Practice
1. Build the planned Node + Postgres project — but add a constraint: implement at least one multi-table transaction with proper rollback handling
2. Read "Database Internals" (Petrov) — chapter 1-3 covers what you need to answer the transaction question confidently
...

---

## What this transcript demonstrates about the system

- **Strategist pivots correctly:** After Turn 2 returned a score of 2 on database topic, the strategist correctly chose `change_topic` rather than probing harder
- **Evaluator scores honesty fairly:** The "I don't know" answers were scored low on content (correctly) but not penalized further on confidence/delivery — they were flagged as `medium` confidence because the candidate was direct, not hedging
- **Coach feedback reflects pattern:** Final report identifies the specific gap (backend/database) rather than just saying "score was 6.3"
