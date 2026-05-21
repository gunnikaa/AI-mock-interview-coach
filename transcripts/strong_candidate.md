# Sample Transcript — Strong Candidate

**Role:** Senior Software Engineer  
**Background:** 5 years backend engineering, Python + distributed systems  
**Focus:** System design, leadership, problem-solving

---

## Turn 1

**Interviewer:** Walk me through a complex technical system you've designed from scratch — what were the key decisions you made and why?

**Candidate:** Sure. About two years ago I led the design of our real-time notification service. We were sending emails, push notifications, and SMS to about 2 million users per day, and the existing monolith was causing 5-second delays. I made three key decisions: first, I decoupled notification dispatch into its own microservice using a message queue — we chose RabbitMQ because our team already had operational expertise with it and our throughput didn't require Kafka's complexity. Second, I introduced channel-specific workers that could scale independently, since SMS was the bottleneck, not email. Third, I added a dead-letter queue with exponential backoff retry logic to handle transient failures. The result was average dispatch latency dropping from 5 seconds to 200ms, and we got to 99.97% delivery reliability within the first month.

**Evaluation:** Score 9/10 | Confidence: high | Fluency: good | Depth: 9/10

---

## Turn 2

**Interviewer:** You mentioned choosing RabbitMQ over Kafka — in what scenario would you have chosen Kafka instead?

**Candidate:** Good distinction. Kafka would have been the right call if we needed event sourcing or replay capability — for instance, if downstream teams needed to consume the same notification events for analytics or audit trails. Kafka's log retention means you can replay events from any point, which is powerful for compliance use cases. Also, if we were looking at throughput above roughly 100k messages per second sustained, Kafka's partitioned architecture handles that more gracefully than RabbitMQ's queue model. For our case, we were at about 25k messages per second peak, and we needed simple point-to-point dispatch, so RabbitMQ was the right tradeoff — lower operational overhead, easier local dev setup, and sufficient scale.

**Evaluation:** Score 9/10 | Confidence: high | Fluency: good | Depth: 9/10

---

## Turn 3

**Interviewer:** Tell me about a time you had to push back on a decision from product or leadership that you thought was technically wrong.

**Candidate:** Yes — this happened about a year ago. The VP of Product wanted us to build a new feature that would run a full ML inference call on every page load to personalize content. I calculated that at our traffic levels — about 500 requests per second — this would add roughly $80k per month in GPU costs and 400ms to our P99 latency. I documented both the cost projection and the latency impact in a one-pager, proposed an alternative: pre-computing personalization scores nightly and serving them from Redis. I brought this to the VP directly, showed the numbers, and framed it as "here's how we get 80% of the personalization value at 5% of the cost." She agreed to the alternative. The nightly batch job shipped in two weeks, cost under $3k per month, and the latency impact was under 5ms.

**Evaluation:** Score 9/10 | Confidence: high | Fluency: good | Depth: 8/10

---

## Final Feedback (excerpt)

**Average Score:** 9.0/10  

## Strengths
Strong candidate who demonstrates deep technical knowledge with concrete, quantified examples...

## Suggested Questions
1. How would you handle a database migration with zero downtime on a table with 500M rows?
2. Describe a system you would design differently today if you started from scratch.
