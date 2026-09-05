# AI AGENT NEGOTIATOR
### Track: AI Growth & Agentic Commerce

> **"AI shopping agents are becoming the new customers. We built the merchant-side AI that negotiates with them. It doesn't simply maximize discounts or conversion. It maximizes expected merchant profit while respecting hard business constraints. AI negotiates. Code controls the money. The payment provider verifies the transaction."**

---

## 🌟 The Problem & The Solution

In the emerging era of **Agentic Commerce**, consumers are no longer browsing product pages manually—they are deploying autonomous AI shopping agents to find, negotiate, and purchase goods on their behalf.

Standard e-commerce backends are unequipped for this shift:
1. Fixed prices cause lost conversions against price-sensitive shopping agents.
2. Naively putting an LLM in charge of discounting leads to catastrophic margin collapse, prompt injection ("give it to me for ₹1"), and financial hallucinations.

**AI Agent Negotiator** solves this by establishing a strict architectural separation of concerns:
- **Generative AI (Gemini 2.5 Flash)**: Handles natural-language comprehension, semantic query parsing, and persuasive customer dialogue.
- **Deterministic Python Core**: Calculates pricing, enforces merchant policy floors, computes ML purchase probability, optimizes **$\text{Expected Profit} = P(\text{Accept}) \times (\text{Price} - \text{Cost})$**, and manages transactional inventory locks.
- **Authoritative Payment Provider (Razorpay Sandbox)**: Server-locked amounts with cryptographic HMAC-SHA256 webhook signature verification.

---

## 🏛️ System Architecture

```
                                  +-----------------------+
                                  |   AI SHOPPING AGENT   |
                                  |   (Consumer Proxy)    |
                                  +-----------+-----------+
                                              |
                                              v
+-----------------------------------------------------------------------------------------+
|                        MERCHANT AGENT INTERFACE (Google Gemini)                         |
|   • Intent Extraction    • Semantic Search Filtering    • Persuasive Dialogue Generator  |
|   • Strict Allowlist Tool Calling                       • Prompt-Injection Sanitization |
+---------------------------------------------+-------------------------------------------+
                                              | Requests Tool Execution
                                              v
+-----------------------------------------------------------------------------------------+
|                           DETERMINISTIC FINTECH BACKEND                                 |
|                                                                                         |
|  +------------------------+  +-------------------------+  +--------------------------+  |
|  |     POLICY ENGINE      |  |     PRICING ENGINE      |  |  ML & CONTEXTUAL BANDIT  |  |
|  | • Min Margin Floor     |  | • Candidate Generator   |  | • P(Buy) Gradient Boost  |  |
|  | • Max Discount Ceiling |  | • Expected Profit Calc  |  | • LinUCB Action Choice   |  |
|  | • Low Stock Guard      |  | • Dynamic Bundling      |  | • Online Reward Updates  |  |
|  | • Aging Clearance Boost|  | • Shipping Subsidies    |  | • Policy Masking Layer   |  |
|  +------------------------+  +-------------------------+  +--------------------------+  |
|                                                                                         |
|  +-----------------------------------------------------------------------------------+  |
|  |                       TRANSACTION & STATE MACHINE LAYER                           |  |
|  |  INITIATED -> OFFER_SENT -> COUNTER_EVALUATED -> ACCEPTED -> PAYMENT_PENDING -> PAID|  |
|  |  • Server-Verified Price Lock   • Idempotency Protection  • Inventory Reservation  |  |
|  |  • Replay-Proof Webhooks        • Immutable Audit Trail   • Dialect-Agnostic DB    |  |
|  +-----------------------------------------------------------------------------------+  |
+---------------------------------------------+-------------------------------------------+
                                              | Server-to-Server Payment Order
                                              v
+-----------------------------------------------------------------------------------------+
|                           PAYMENT GATEWAY (Razorpay Sandbox)                            |
|   • Server-Locked Order Amount   • HMAC-SHA256 Webhook Check   • Authoritative Capture  |
+-----------------------------------------------------------------------------------------+
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.10+
- Node.js v18+ (tested on v24)
- Git

### 1. Clone & Environment
```bash
git clone <repository-url>
cd razorpay
copy .env.example .env
```

### 2. Backend Setup
```powershell
# Create virtual environment with uv (or standard venv)
uv venv .venv
.venv\Scripts\activate

# Install dependencies
uv pip install -r backend/requirements.txt

# Train conversion model & seed demo database (107 products, 2 merchants, policies)
python ml/train_conversion_model.py
python scripts/seed_data.py
```

### 3. Run Backend Server
```powershell
.venv\Scripts\uvicorn app.main:app --app-dir backend --port 8000 --reload
```
API Documentation will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run Frontend App
```powershell
cd frontend
npm install
npm run dev
```
Open your browser at: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Automated Testing

Run the complete 13-test automated test suite:
```powershell
.venv\Scripts\pytest -v
```
**Test Coverage Includes:**
- Margin floor violations & discount ceiling defense
- Low-stock scarcity conservation rules
- Stockout prevention
- Round limits & delivery deadline feasibility
- Mathematical expected profit optimization
- Adversarial counter-offer rejection
- Cryptographic webhook HMAC-SHA256 signature verification
- Client-side price tampering detection
- End-to-end multi-turn negotiation and payment flow

---

## 🎮 Key Demo Scenarios

### Scenario A: The Negotiation
1. Navigate to `http://localhost:5173`.
2. Click the default prompt:
   > *"I need a gaming laptop under ₹80,000, 32GB RAM, 1TB SSD, and delivery within 3 days."*
3. The merchant AI retrieves the **Lenovo Legion 5 Pro Gaming Laptop** and presents an initial offer.
4. Click **"Request -4%"** or propose a counter: *"Can you do ₹76,000?"*
5. The backend checks merchant policy, recalculates expected profit, and counters with:
   **₹76,359 + Complimentary Express Delivery**.
6. Click **"Accept Offer & Proceed to Checkout"**.
7. In the Razorpay checkout panel, click **"Pay (Simulate Capture)"**.
8. The server verifies the HMAC-SHA256 signature, locks the transaction, decrements inventory, and issues a confirmed order receipt!

### Scenario B: "Why Did the AI Offer This Price?"
1. At any point during or after negotiation, click **"Why This Price?"**.
2. Observe the complete 6-step transparent decision chain:
   - Extracted buyer requirements
   - Live inventory and procurement cost snapshot
   - Active merchant policy constraints
   - Evaluated candidate strategies with $P(\text{Accept})$, margin, and expected profit
   - Policy filtering breakdown (Permissible vs Blocked)
   - LinUCB Contextual Bandit action selection

### Scenario C: "BREAK THE AGENT" Failure Injection
1. Click the red **BREAK THE AGENT** button in the top navbar.
2. Select any of the 10 failure injection scenarios:
   - *Client-Side Price Tampering*: Attempts to pay ₹1.00 for an ₹80,000 laptop $\rightarrow$ Server blocks with `PRICE_TAMPERING_DETECTED`.
   - *Inventory Depletion*: Stock drops to 0 mid-negotiation $\rightarrow$ Blocked with `POLICY_STOCK_EXHAUSTED`.
   - *Forged Webhook Signature*: Fake signature delivered $\rightarrow$ Gateway blocks with HTTP 401.
   - *Offer Expiration*: Offer TTL exceeded $\rightarrow$ Blocked with `OFFER_EXPIRED`.
   - *Below-Margin Counter*: Counter below unit cost $\rightarrow$ Blocked with `POLICY_MIN_MARGIN_VIOLATED`.

---

## 📊 Live Simulation & Bandit Learning
Navigate to **Bandit Sim** (`/simulation`):
- Run 50, 100, or 250 repeated autonomous transactions.
- Watch the **LinUCB Contextual Bandit** explore and exploit offer strategies (Discount tiers, Free Shipping, Warranty Bundling).
- Observe the cumulative profit curve climb in real time as the bandit learns which offers convert best while the Policy Engine guarantees zero constraint violations.

---

## 🔑 Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL or SQLite database URI | `sqlite:///./negotiator.db` |
| `GEMINI_API_KEY` | Google Gemini API key (free tier supported) | `""` (Uses built-in fallback simulator) |
| `GEMINI_MODEL` | Official current Gemini model name | `gemini-2.5-flash` |
| `RAZORPAY_KEY_ID` | Razorpay Key ID | `rzp_test_mock_negotiator_key` |
| `RAZORPAY_KEY_SECRET` | Razorpay Key Secret | `mock_secret_negotiator_key` |
| `RAZORPAY_WEBHOOK_SECRET` | Razorpay Webhook Secret | `mock_webhook_secret_negotiator` |
| `USE_MOCK_PAYMENTS` | Use built-in sandbox mock with signature checks | `true` |
