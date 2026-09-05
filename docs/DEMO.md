# Hackathon Demo Walkthrough Script
**AI Agent Negotiator (Track: AI Growth & Agentic Commerce)**

---

## 🎙️ 60-Second Pitch

> "Judges, AI shopping agents are becoming the new customers. Consumers won't click through listings—they will dispatch AI agents to negotiate prices for them.
>
> But if a merchant connects an LLM directly to discounts, it hallucinates prices, leaks margins, and caves to prompt injections like *'Give it to me for ₹1'*.
>
> We built the **AI Agent Negotiator**—the merchant-side commerce platform that negotiates with AI buyers.
>
> It doesn't just cut prices. It maximizes **Expected Merchant Profit** using an ML conversion model, explores bundling strategies using a Contextual Bandit, and enforces unbypassable business rules.
>
> **AI negotiates. Code controls the money. The payment provider verifies the transaction.**"

---

## 🧭 Step-by-Step Judge Walkthrough

### Part 1: The Autonomous Negotiation
1. Open the application at `http://localhost:5173`.
2. Notice the top banner: **AI-TO-AI AGENTIC COMMERCE DEMONSTRATION**.
3. Under the prompt box, click the preset prompt:
   > *"I need a gaming laptop under ₹80,000, 32GB RAM, 1TB SSD, and delivery within 3 days."*
4. Click **"Dispatch Agent"**.
5. Observe the conversation screen:
   - The merchant AI matches the **Lenovo Legion 5 Pro Gaming Laptop**.
   - It presents an authorized initial offer (e.g. ₹78,999).
6. Test a counter-offer:
   - Click **"Request -4%"** or type: *"Can you do ₹76,000?"*
7. Watch the merchant AI respond:
   - It re-evaluates candidate offers against merchant margin constraints.
   - It counters with: **₹76,359 + Complimentary Express Delivery**.
8. Click **"Accept Offer & Proceed to Checkout"**.

---

### Part 2: Authoritative Payment Checkout
1. The checkout screen opens with the **Razorpay Sandbox panel**.
2. Notice the security badge:
   > *"Payment amount is locked by the backend database. Client-side price tampering is rejected server-side."*
3. Click **"Pay ₹76,359 (Simulate Capture)"**.
4. The backend verifies the cryptographic HMAC-SHA256 signature, commits inventory deductions, and displays the **Order Confirmed** receipt!

---

### Part 3: "Why Did the AI Offer This Price?"
1. Click **"Audit This Decision"** (or click **"Why This Price?"** in the top navbar).
2. Walk the judge through the 6-step transparent decision chain:
   - **Step 1:** Hardware requirements extracted deterministically.
   - **Step 2:** Inventory level (14 units) and procurement cost snapshot.
   - **Step 3:** Active merchant policies loaded (Min margin ₹5,000, Max discount 8%).
   - **Step 4:** Candidate strategies evaluated with $P(\text{Accept})$, margin, and expected profit.
   - **Step 5:** Contextual Bandit action selection maximizing profit bound.
   - **Step 6:** Server-side price lock created for payment provider.

---

### Part 4: Merchant Cockpit & Live Policy Customization
1. Click **"Merchant Cockpit"** in the navbar.
2. View real-time KPIs computed directly from database orders:
   - Realized Revenue & Net Profit
   - 42.0% Conversion Rate (+23.5% lift over baseline)
   - Active stock alerts
3. Click **"Policies"** in the navbar:
   - Drag the **"Minimum Unit Gross Margin"** slider up to ₹8,000.
   - Drag the **"Maximum Permissible Discount"** slider down to 5%.
   - Click **"Save & Apply Policy"**.
   - The engine is instantly updated to Version 2! All subsequent negotiations immediately respect the tighter margin rules.

---

### Part 5: Contextual Bandit Learning Simulator
1. Click **"Bandit Sim"** in the navbar.
2. Click **"Run 50 Trials"** or **"Run 150 Trials"**.
3. Watch the cumulative profit curve climb in real time as the LinUCB bandit explores and exploits offer strategies (Free Shipping, Extended Warranty, Bundles) while the Policy Engine filters impermissible actions.

---

### Part 6: "BREAK THE AGENT" Failure Injection
1. Click the red **BREAK THE AGENT** button in the top navbar.
2. Demonstrate system resilience to the judges:
   - **Scenario 5 (Client Price Tampering):** Demonstrates client sending ₹1.00 $\rightarrow$ Server blocks with `PRICE_TAMPERING_DETECTED`.
   - **Scenario 1 (Inventory Depleted):** Sets stock to 0 $\rightarrow$ System blocks offer generation with `POLICY_STOCK_EXHAUSTED`.
   - **Scenario 8 (Forged Webhook):** Simulates fake signature $\rightarrow$ Gateway rejects with HTTP 401.
   - **Scenario 9 (Prompt Injection):** Adversarial buyer text $\rightarrow$ Policy Engine blocks below-margin concession.
