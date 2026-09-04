<div align="center">
  <br />
  <h1>⚡ Razorpay Relay</h1>
  <p>
    <strong>Autonomous AI Revenue Recovery Engine</strong>
  </p>
  <p>
    Detect · Diagnose · Decide · Act · Observe · Replan<br />
    Across <strong>B2C consumer payments</strong> and <strong>B2B receivables</strong>
  </p>

  <p>
    <img src="https://img.shields.io/badge/B2C-Failed%20Payments%20·%20Carts%20·%20Subscriptions-2B84EA?style=for-the-badge" alt="B2C" />
    <img src="https://img.shields.io/badge/B2B-Overdue%20Receivables%20·%20Collections-F59E0B?style=for-the-badge" alt="B2B" />
  </p>

  <p>
    <img src="https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js" alt="Next.js" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-FF4F00?style=flat-square&logo=langchain&logoColor=white" alt="LangGraph" />
    <img src="https://img.shields.io/badge/React%20Flow-Live%20Graph-8B5CF6?style=flat-square" alt="React Flow" />
    <img src="https://img.shields.io/badge/Razorpay-02042B?style=flat-square&logo=razorpay&logoColor=white" alt="Razorpay" />
  </p>
</div>

---

## 🎯 What is Razorpay Relay?

**Razorpay Relay** is a closed-loop, multi-agent system that finds revenue slipping away and works to win it back — not with static drip reminders, but with adaptive AI that remembers previous attempts, observes outcomes, and replans when an intervention fails.

| Segment | Revenue at risk | How Relay recovers it |
|---------|-----------------|------------------------|
| **B2C** | Failed payments, abandoned checkouts, subscription renewals | Investigate transaction + customer context → retry, payment link, email/WhatsApp, discount, or stop |
| **B2B** | Overdue invoices & receivables | Age the invoice → score payment history → plan remind / wait / escalate / stop → collections tone + audit trail |

> Traditional tools apply the **same reminder sequence** to every failure.<br />
> Relay chooses the **right intervention for this case, right now** — then learns from the outcome.

---

## 💥 The Problem We Solve

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'fontFamily': 'Segoe UI', 'primaryTextColor': '#F8FAFC'}}}%%
flowchart LR
  subgraph BLEED["💸 Revenue Leakage"]
    A["💳 Failed payment"]
    B["🛒 Abandoned cart"]
    C["🔄 Subscription lapse"]
    D["📄 Unpaid invoice"]
  end

  subgraph OLD["❌ Static Drip Systems"]
    E["Fixed rules"]
    F["Same email sequence"]
    G["No memory of outcomes"]
    H["Spam or silence"]
  end

  subgraph RELAY["✅ Razorpay Relay"]
    I["Context-aware agents"]
    J["Adaptive strategy"]
    K["Closed-loop replan"]
    L["Bounded autonomy"]
  end

  BLEED --> OLD
  BLEED --> RELAY

  classDef bleed fill:#7F1D1D,stroke:#EF4444,color:#FFF
  classDef old fill:#374151,stroke:#9CA3AF,color:#E5E7EB
  classDef relay fill:#064E3B,stroke:#22C55E,color:#FFF
  class BLEED bleed
  class OLD old
  class RELAY relay
```

Revenue loss rarely happens in one predictable step. A bank timeout, a distracted shopper, a failed renewal, or a 45-day overdue invoice each need a **different** response. Static systems cannot diagnose root cause, respect cooldowns intelligently, or escalate only when it is worth it.

**Relay closes the loop.**

---

## 🆚 What Makes Relay Different

| Capability | Traditional recovery | Razorpay Relay |
|------------|----------------------|----------------|
| Decisioning | If/else + drip timers | Multi-agent LangGraph orchestration |
| Context | Amount + template | History, signals, aging, response behavior |
| Memory | Stateless campaigns | Remembers attempts, outcomes, replans |
| B2C + B2B | Usually separate products | One engine, dual specialist paths |
| Safety | Soft limits (or none) | Deterministic **Policy Engine** (non-LLM) |
| Observability | Logs after the fact | **Live Agent Graph** + SSE console |
| Stopping rules | Rarely enforced | Attempt caps, cooldowns, escalate / stop |

---

## 🧬 Dual-Segment Product Model

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
  EVT["📥 Revenue Risk Event"] --> SENT["⚡ Revenue Sentinel"]
  SENT --> CLASS["🔍 Leakage Classifier"]

  CLASS -->|"B2C"| B2C["🔵 Consumer Recovery Path"]
  CLASS -->|"B2B"| B2B["🟠 Receivables Path"]

  B2C --> S1["Failed Payment"]
  B2C --> S2["Abandoned Cart"]
  B2C --> S3["Subscription"]

  B2B --> R1["Overdue Receivable Specialist"]
  R1 --> R2["Invoice Analyzer"]
  R2 --> R3["History Analyst"]
  R3 --> R4["Follow-up Planner"]

  S1 & S2 & S3 & R4 --> STRAT["🧠 Recovery Strategist"]
  STRAT --> POL["🛡️ Policy Engine"]
  POL -->|Approve| EXEC["⚡ Execution"]
  POL -->|Block| REPLAN["♻️ Replan"]
  REPLAN --> STRAT
  EXEC --> MON["👁 Monitor"]
  MON --> ENDN["✅ Recovered / Waiting / Stopped"]

  classDef entry fill:#1E3A5F,stroke:#2B84EA,color:#FFF
  classDef b2c fill:#1E3A8A,stroke:#60A5FA,color:#FFF
  classDef b2b fill:#78350F,stroke:#F59E0B,color:#FFF
  classDef brain fill:#4C1D95,stroke:#A78BFA,color:#FFF
  classDef policy fill:#854D0E,stroke:#EAB308,color:#FFF
  classDef ok fill:#14532D,stroke:#22C55E,color:#FFF

  class EVT,SENT,CLASS entry
  class B2C,S1,S2,S3 b2c
  class B2B,R1,R2,R3,R4 b2b
  class STRAT,EXEC,MON brain
  class POL,REPLAN policy
  class ENDN ok
```

---

## 🕸️ Live Agent Graph (Full Topology)

This is the **exact LangGraph topology** rendered live in the Command Center (React Flow + SSE).

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'fontFamily': 'Segoe UI', 'lineColor': '#94A3B8'}}}%%
flowchart TB
  START((🚀 Start)) --> SENT["⚡ Revenue Sentinel"]
  SENT --> CLASS["🔍 Leakage Classifier"]

  CLASS -->|FAILED_PAYMENT| FP["💳 Failed Payment Specialist"]
  CLASS -->|ABANDONED_CART| AC["🛒 Cart Specialist"]
  CLASS -->|SUBSCRIPTION_FAILURE| SUB["🔄 Subscription Specialist"]
  CLASS -->|OVERDUE_RECEIVABLE| ORS["📄 Overdue Receivable Specialist"]

  ORS --> INV["📊 Invoice Analyzer<br/><i>B2B sub-node</i>"]
  INV --> HIST["📈 History Analyst<br/><i>B2B sub-node</i>"]
  HIST --> PLAN["🗓️ Follow-up Planner<br/><i>B2B sub-node</i>"]

  FP --> STRAT
  AC --> STRAT
  SUB --> STRAT
  PLAN --> STRAT["🧠 Recovery Strategist"]

  STRAT --> POL["🛡️ Policy Engine"]
  POL -->|approved| EXEC["⚡ Execution Agent"]
  POL -->|blocked| REPLAN["♻️ Replan"]
  REPLAN --> STRAT
  POL -->|limits exceeded| ESC["🚨 Escalate"]

  EXEC --> MON["👁 Monitor Agent"]
  MON --> END1((✅ End / Wait for payment))
  ESC --> END2((🛑 Escalated))

  classDef start fill:#0F172A,stroke:#F8FAFC,color:#F8FAFC,stroke-width:2px
  classDef shared fill:#1E40AF,stroke:#93C5FD,color:#FFF,stroke-width:2px
  classDef b2c fill:#0369A1,stroke:#38BDF8,color:#FFF,stroke-width:2px
  classDef b2b fill:#B45309,stroke:#FCD34D,color:#FFF,stroke-width:2px
  classDef sub fill:#92400E,stroke:#FBBF24,color:#FFF,stroke-width:1px
  classDef ai fill:#6D28D9,stroke:#C4B5FD,color:#FFF,stroke-width:2px
  classDef guard fill:#A16207,stroke:#FDE047,color:#111,stroke-width:2px
  classDef endn fill:#15803D,stroke:#86EFAC,color:#FFF,stroke-width:2px
  classDef danger fill:#B91C1C,stroke:#FCA5A5,color:#FFF,stroke-width:2px

  class START,END1,END2 start
  class SENT,CLASS,EXEC,MON shared
  class FP,AC,SUB b2c
  class ORS b2b
  class INV,HIST,PLAN sub
  class STRAT ai
  class POL,REPLAN guard
  class ESC danger
```

**Legend**

| Color | Meaning |
|-------|---------|
| 🔵 Blue | Shared pipeline / B2C specialists |
| 🟠 Amber | B2B receivables specialist + sub-nodes |
| 🟣 Purple | AI strategist decisions |
| 🟡 Gold | Deterministic policy / replan |
| 🟢 Green | Terminal success / wait |
| 🔴 Red | Human escalation |

---

## 🧩 UML — Component Architecture

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
  subgraph UI["🖥️ Presentation Layer — Next.js"]
    P1["Trigger Event Form<br/>B2C / B2B toggle"]
    P2["Live Agent Graph<br/>React Flow"]
    P3["Decision Panel"]
    P4["Recovery Queue"]
    P5["Case Details"]
    P6["Live Orchestration Console"]
    P7["Revenue Metrics"]
  end

  subgraph API["⚡ API Layer — FastAPI"]
    A1["POST /recovery/start"]
    A2["POST /recovery/batch"]
    A3["GET /recovery/{id}/stream  SSE"]
    A4["GET /dashboard/*"]
    A5["Webhooks / payment"]
  end

  subgraph ORCH["🧠 Orchestration — LangGraph"]
    O1["RecoveryState"]
    O2["StateGraph nodes"]
    O3["Conditional routing"]
    O4["Event Bus"]
  end

  subgraph DATA["🗄️ Persistence"]
    D1["RecoveryCase"]
    D2["RevenueEvent"]
    D3["Customer"]
    D4["PaymentLink / Communication"]
  end

  subgraph EXT["🌐 Providers"]
    E1["Razorpay / Mock Payments"]
    E2["Resend / Mock Email"]
    E3["LLM OpenAI-compatible"]
  end

  P1 & P2 & P3 & P4 & P5 & P6 & P7 <--> API
  API --> ORCH
  ORCH --> DATA
  ORCH --> EXT
  A3 -.->|SSE events| P2
  A3 -.->|SSE events| P6

  classDef ui fill:#111827,stroke:#2B84EA,color:#E2E8F0
  classDef api fill:#0C4A6E,stroke:#38BDF8,color:#FFF
  classDef orch fill:#4C1D95,stroke:#C4B5FD,color:#FFF
  classDef data fill:#14532D,stroke:#4ADE80,color:#FFF
  classDef ext fill:#7C2D12,stroke:#FB923C,color:#FFF

  class UI ui
  class API api
  class ORCH orch
  class DATA data
  class EXT ext
```

---

## 📐 UML — Sequence (B2C Failed Payment)

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
  autonumber
  participant U as Dashboard / Merchant
  participant API as FastAPI
  participant G as LangGraph
  participant S as Sentinel
  participant C as Classifier
  participant F as Failed Payment Specialist
  participant R as Strategist
  participant P as Policy
  participant E as Execution
  participant M as Monitor
  participant Pay as Payment Provider

  U->>API: POST /recovery/start (B2C signals)
  API->>API: Create case + emit case_created
  API->>G: ainvoke(RecoveryState)
  G->>S: Assess revenue risk / priority
  S->>C: Classify leakage
  C->>F: FAILED_PAYMENT
  F->>F: Customer history + root cause
  F->>R: Investigation
  R->>R: Evaluate ≥3 alternatives
  R->>P: Proposed strategy
  alt Policy approved
    P->>E: Execute (link + email/WhatsApp/retry)
    E->>Pay: create_payment_link
    E->>M: WAITING_FOR_PAYMENT
  else Policy blocked
    P->>R: Replan (loop)
  end
  API-->>U: SSE stream (live graph updates)
```

---

## 📐 UML — Sequence (B2B Overdue Receivable)

```mermaid
%%{init: {'theme': 'dark'}}%%
sequenceDiagram
  autonumber
  participant U as Dashboard
  participant API as FastAPI
  participant G as LangGraph
  participant OR as Overdue Receivable
  participant IA as Invoice Analyzer
  participant HA as History Analyst
  participant FP as Follow-up Planner
  participant R as Strategist
  participant P as Policy
  participant E as Execution

  U->>API: POST /recovery/start (invoice + B2B signals)
  API->>G: Run graph (segment=B2B)
  G->>OR: Seed investigation (aging, follow-ups, response)
  OR->>IA: Analyze aging bucket + invoice tier + tone
  IA->>HA: Score reliability + risk flags
  HA->>FP: Decide REMIND / WAIT / ESCALATE / STOP
  FP->>R: Follow-up plan + investigation
  R->>R: Map to SEND_INVOICE_REMINDER / WAIT / …
  R->>P: B2B policy (higher amount cap, no discounts, follow-up limits)
  alt Approved reminder
    P->>E: Payment link + collections email
  else Wait / cooldown
    P->>E: Schedule follow-up (N hours)
  else Escalate / Stop
    P->>E: Human handoff or stop
  end
  API-->>U: Live graph lights B2B sub-nodes (amber)
```

---

## 🔵 B2C — Consumer Payment Recovery

### How we solve B2C leakage

1. **Detect** risk signals (failed charge, checkout abandoned, renewal failed).
2. **Diagnose** with a specialist that understands that failure mode.
3. **Decide** channel + action (retry, link, email, WhatsApp, discount, stop).
4. **Guard** with policy (retry caps, message frequency, amount limits).
5. **Act** via real tools (payment link + communication).
6. **Observe** and wait for payment webhook; replan if needed.

### B2C agents — what each one does

| Agent | Role | Key outputs |
|-------|------|-------------|
| **Revenue Sentinel** | First triage — is revenue at risk? How urgent? | `amount_at_risk`, priority, urgency, recovery probability |
| **Leakage Classifier** | Route by signals (with hard overrides) | `FAILED_PAYMENT` / `ABANDONED_CART` / `SUBSCRIPTION_FAILURE` |
| **Failed Payment Specialist** | Root-cause bank/card failures + customer value | Root cause, value tier, confidence |
| **Abandoned Cart Specialist** | Intent vs friction (price, shipping, distraction) | Cart context, approach |
| **Subscription Specialist** | Renewal / churn context | Billing failure context |
| **Recovery Strategist** | Pick optimal action + write copy | Primary action, channel, alternatives |
| **Policy Engine** | Non-LLM guardrails | Approve / block + violations |
| **Execution Agent** | Call tools | Payment link, email, WhatsApp, retry |
| **Monitor Agent** | Wait / verify outcome | `WAITING_FOR_PAYMENT` → recovered via webhook |

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
  subgraph B2C_FLOW["🔵 B2C Path"]
    direction TB
    C["Classifier"] --> FP["Failed Payment"]
    C --> AC["Abandoned Cart"]
    C --> SU["Subscription"]
    FP & AC & SU --> ST["Strategist"]
    ST --> PO["Policy"]
    PO --> EX["Execute"]
    EX --> MO["Monitor"]
  end

  classDef n fill:#1D4ED8,stroke:#93C5FD,color:#FFF
  class C,FP,AC,SU,ST,PO,EX,MO n
```

### B2C actions the strategist can choose

`SMART_RETRY` · `CREATE_PAYMENT_LINK` · `SEND_EMAIL` · `SEND_WHATSAPP` · `OFFER_DISCOUNT` · `WAIT` · `ESCALATE_TO_HUMAN` · `STOP`

---

## 🟠 B2B — Receivables & Collections

### How we solve B2B leakage

Overdue invoices are not “failed checkouts.” They need **collections intelligence**:

1. **Age** the invoice (1–30 / 31–60 / 61–90 / 90+).
2. **Tier** by value (HIGH / MEDIUM / LOW).
3. **Read history** — on-time rate, prior follow-ups, response pattern.
4. **Plan** — remind, wait (cooldown), escalate (dispute / stuck high-value), or stop (max attempts).
5. **Act** with professional collections tone + payment link.
6. **Bound** autonomy — max follow-ups, no consumer-style discounts, higher auto amount caps, full audit trail.

### B2B agents — parent + sub-nodes

| Agent | Type | Role |
|-------|------|------|
| **Overdue Receivable Specialist** | Parent | Seeds B2B investigation from invoice + signals |
| **Invoice Analyzer** | Sub-node | Aging bucket, invoice tier, urgency, recommended tone |
| **History Analyst** | Sub-node | Payer reliability, risk flags, response pattern |
| **Follow-up Planner** | Sub-node | `REMIND` / `WAIT` / `ESCALATE` / `STOP` (+ cooldown hours) |
| *(then shared)* Strategist → Policy → Execution → Monitor | Shared | Convert plan into executable strategy under B2B rules |

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart TB
  ORS["📄 Overdue Receivable Specialist"] --> IA["📊 Invoice Analyzer"]
  IA --> HA["📈 History Analyst"]
  HA --> FP["🗓️ Follow-up Planner"]

  FP -->|REMIND| REM["SEND_INVOICE_REMINDER"]
  FP -->|WAIT| WAIT["SCHEDULE_FOLLOWUP / WAIT"]
  FP -->|ESCALATE| ESC["ESCALATE_TO_HUMAN"]
  FP -->|STOP| STOP["STOP"]

  classDef parent fill:#B45309,stroke:#FCD34D,color:#FFF,stroke-width:3px
  classDef sub fill:#92400E,stroke:#FBBF24,color:#FFF
  classDef act fill:#78350F,stroke:#F59E0B,color:#FFF

  class ORS parent
  class IA,HA,FP sub
  class REM,WAIT,ESC,STOP act
```

### B2B-specific actions

`SEND_INVOICE_REMINDER` · `SCHEDULE_FOLLOWUP` · `CREATE_PAYMENT_LINK` · `WAIT` · `ESCALATE_TO_HUMAN` · `STOP`

### B2B policy differences

| Guardrail | B2C | B2B |
|-----------|-----|-----|
| Max auto amount | ₹50,000 | ₹500,000 |
| Discounts | Allowed (≤10%) | Blocked |
| Follow-up cap | Message/day limits | Max follow-ups (e.g. 5) + cooldowns |
| Tone | Consumer recovery | Collections (soft → firm → escalate) |

---

## 🧠 Agent Reference Card (All Nodes)

```mermaid
%%{init: {'theme': 'dark'}}%%
mindmap
  root((Razorpay Relay))
    Shared
      Revenue Sentinel
      Leakage Classifier
      Recovery Strategist
      Policy Engine
      Execution Agent
      Monitor Agent
      Replan
      Escalate
    B2C Specialists
      Failed Payment
      Abandoned Cart
      Subscription
    B2B Specialists
      Overdue Receivable
      Invoice Analyzer
      History Analyst
      Follow-up Planner
```

### Shared pipeline (detail)

| # | Node | LLM? | Responsibility |
|---|------|------|----------------|
| 1 | **Revenue Sentinel** | Yes | Detect risk, score urgency & recoverability |
| 2 | **Leakage Classifier** | Yes + rules | Categorize + hard signal overrides (incl. B2B invoice) |
| 3 | **Recovery Strategist** | Yes | Multi-option strategy, copy, channel |
| 4 | **Policy Engine** | **No** | Hard business constraints — cannot be overridden by the LLM |
| 5 | **Execution Agent** | Tools | Payment links, email, WhatsApp, retries, schedule follow-up |
| 6 | **Monitor Agent** | Light | Waiting state; payment webhooks complete recovery |
| 7 | **Replan** | Control | Increment replan count → back to Strategist |
| 8 | **Escalate** | Control | Hand off to human when autonomy is exhausted |

> **Bounded autonomy**: the Policy Engine is intentionally deterministic. AI proposes; rules dispose.

---

## 🔄 Closed-Loop State Machine (UML)

```mermaid
%%{init: {'theme': 'dark'}}%%
stateDiagram-v2
  [*] --> CREATED: Event ingested
  CREATED --> PROCESSING: Graph starts
  PROCESSING --> WAITING_FOR_PAYMENT: Link / reminder sent
  PROCESSING --> WAITING_FOR_PAYMENT: Follow-up scheduled
  PROCESSING --> ESCALATED: Limits / dispute
  PROCESSING --> FAILED: STOP / hard fail
  WAITING_FOR_PAYMENT --> RECOVERED: Payment webhook
  WAITING_FOR_PAYMENT --> PROCESSING: Replan (optional)
  ESCALATED --> [*]
  RECOVERED --> [*]
  FAILED --> [*]

  note right of PROCESSING
    Agents emit SSE events
    Live graph updates node status
  end note
```

---

## 🏗️ System Architecture

```mermaid
%%{init: {'theme': 'dark'}}%%
flowchart LR
  subgraph FE["Frontend"]
    UI["Next.js Command Center"]
  end

  subgraph BE["Backend"]
    API["FastAPI"]
    LG["LangGraph Engine"]
    BUS["In-memory Event Bus"]
    DB[(SQLite)]
  end

  subgraph OUT["Side effects"]
    PAY["Payment Provider"]
    MAIL["Email / WhatsApp"]
    LLM["LLM API"]
  end

  UI <-->|REST| API
  UI <-->|SSE| BUS
  API --> LG
  LG --> BUS
  LG --> DB
  LG --> LLM
  LG --> PAY
  LG --> MAIL

  classDef fe fill:#020617,stroke:#2B84EA,color:#FFF
  classDef be fill:#1E1B4B,stroke:#A78BFA,color:#FFF
  classDef out fill:#14532D,stroke:#4ADE80,color:#FFF
  class FE,UI fe
  class BE,API,LG,BUS,DB be
  class OUT,PAY,MAIL,LLM out
```

---

## 🎬 Scenarios

### B2C — VIP failed payment
**Trigger:** High-LTV customer, `insufficient_funds`.<br />
**Path:** Classifier → Failed Payment Specialist → Strategist prefers soft `CREATE_PAYMENT_LINK` + email (no harsh tone).<br />
**Result:** Loyalty preserved; payment recovered via link.

### B2C — Abandoned cart
**Trigger:** Checkout started, payment never attempted, inactive 120m.<br />
**Path:** Cart Specialist → Strategist → link + reminder (optional small discount if policy allows).

### B2B — Acknowledged but unpaid
**Trigger:** Invoice 32d overdue, 1 prior follow-up, response = `acknowledged`.<br />
**Path:** Receivable → Invoice Analyzer → History → Follow-up Planner chooses **WAIT** (cooldown) → Execution schedules follow-up.<br />
**Why different:** Nagging an acknowledged buyer reduces recovery and damages the relationship.

### B2B — Disputed invoice
**Trigger:** `response_behavior = disputed`.<br />
**Path:** Follow-up Planner hard-escalates → human collections.<br />
**Why different:** Autonomy stops; disputes need people.

### B2B — Silent overdue, high value
**Trigger:** ₹1,49,999, 75d overdue, ignored reminders.<br />
**Path:** Firm tone reminder or escalate per history + attempt count; policy blocks spam.

---

## 🖥️ Command Center (Frontend)

| Panel | Purpose |
|-------|---------|
| **Trigger form** | Toggle **B2C / B2B**, fire single or batch test events |
| **Live Agent Graph** | Watch nodes turn ACTIVE → COMPLETED (B2B sub-nodes in amber) |
| **Decision Panel** | Selected strategy + alternatives with probabilities |
| **Queue / Case Details** | Segment badge, category, invoice, follow-up plan |
| **Live Console** | SSE orchestration log (agents, tools, decisions, policy) |

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- OpenAI-compatible API key

### 1. Backend
```bash
cd recover-ai/backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # set OPENAI_API_KEY (and optional base URL)
python run.py          # http://localhost:8000
```

### 2. Frontend
```bash
cd recover-ai/frontend
npm install
npm run dev            # http://localhost:3000
```

### 3. Try B2B in 30 seconds
1. Open the dashboard → **B2B Receivables**
2. Click **START B2B COLLECTIONS**
3. Watch the live graph: **Overdue Receivable → Invoice Analyzer → History Analyst → Follow-up Planner → Strategist → …**

### 4. Try B2C
1. Switch to **B2C Consumer**
2. Use abandoned-cart or failed-payment signals
3. Watch the blue specialist path light up

---

## 📦 Project Layout

```
recover-ai/
├── backend/
│   └── app/
│       ├── agents/          # Sentinel, classifier, B2C + B2B specialists, strategist, execution, monitor
│       ├── graph/           # StateGraph, routing, RecoveryState
│       ├── policies/        # Deterministic Policy Engine
│       ├── api/             # REST + SSE + webhooks
│       ├── services/        # Orchestration, providers, event bus
│       └── schemas/         # Events, agent outputs, cases
└── frontend/
    ├── components/agent/    # Live Agent Graph, console, decision panel
    ├── components/recovery/ # Trigger (B2C/B2B), queue, case details
    └── hooks/               # SSE recovery stream
```

---

## ✨ Summary

**Razorpay Relay** turns revenue recovery from a static reminder workflow into an **adaptive multi-agent system**:

- **B2C** recovers failed payments, carts, and subscriptions with context-aware interventions  
- **B2B** runs a full receivables sub-graph (analyze → history → plan) before acting  
- **Policy** keeps autonomy bounded  
- **Live Agent Graph** makes every decision and sub-node visible in real time  

> Detect → Diagnose → Decide → Act → Observe → Replan — with measurable revenue recovered.

---

<div align="center">
  <p><strong>Razorpay Relay</strong> — Autonomous recovery for consumer payments & B2B receivables.</p>
  <p>Built with LangGraph · FastAPI · Next.js · React Flow</p>
</div>
