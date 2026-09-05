# Payment Gateway Integration Guide
**Razorpay Sandbox & Production Architecture**

## 1. Overview

The AI Agent Negotiator integrates with **Razorpay** as the authoritative payment gateway. All financial state transitions (transitioning from `PAYMENT_PENDING` to `PAID`) require server-side verification from Razorpay or an authorized cryptographic webhook.

---

## 2. Gateway Architecture

The system utilizes an abstract provider interface:

```python
class PaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, order_id, amount, currency, metadata) -> PaymentSession:
        """Creates an order on the payment gateway."""
        pass

    @abstractmethod
    def get_payment(self, payment_id) -> PaymentStatus:
        """Queries the gateway directly for authoritative payment status."""
        pass

    @abstractmethod
    def verify_webhook(self, payload_body, signature, secret) -> bool:
        """Verifies HMAC-SHA256 signature on incoming webhook."""
        pass

    @abstractmethod
    def capture_payment(self, payment_id, amount, currency) -> bool:
        """Captures authorized funds."""
        pass

    @abstractmethod
    def refund_payment(self, payment_id, amount) -> bool:
        """Executes full or partial refund."""
        pass
```

Two provider implementations are included:
1. **`RazorpayPaymentProvider`**: Uses the official Razorpay Python SDK with active API keys for test and production environments.
2. **`MockSandboxProvider`**: A zero-configuration mock gateway providing exact Razorpay response envelopes, HMAC-SHA256 signature calculation, and simulated webhook delivery for hackathon evaluation without external network dependencies.

---

## 3. Configuring Live Razorpay Sandbox

To switch from the built-in mock to your own Razorpay test account:

### Step 1: Obtain Razorpay Test Keys
1. Log in to your [Razorpay Dashboard](https://dashboard.razorpay.com/).
2. Switch to **Test Mode** (toggle in the top-left).
3. Navigate to **Settings $\rightarrow$ API Keys $\rightarrow$ Generate Key**.
4. Note your `Key ID` and `Key Secret`.

### Step 2: Configure Webhooks
1. In the Razorpay Dashboard, navigate to **Settings $\rightarrow$ Webhooks $\rightarrow$ Add New Webhook**.
2. Enter your Webhook URL: `https://your-domain.com/api/payments/webhook` (or use Ngrok for local testing).
3. Enter a Secret: e.g. `your_custom_webhook_secret_here`.
4. Select active events:
   - `payment.authorized`
   - `payment.captured`
   - `payment.failed`
   - `order.paid`

### Step 3: Set Environment Variables
In your `.env` file:
```env
RAZORPAY_KEY_ID=rzp_test_your_key_here
RAZORPAY_KEY_SECRET=your_key_secret_here
RAZORPAY_WEBHOOK_SECRET=your_custom_webhook_secret_here
USE_MOCK_PAYMENTS=false
```
Restart the backend. All payment creation, checkout, and webhook verification will now execute live against Razorpay test servers!

---

## 4. Webhook Security Checklist

- [x] Webhook endpoint `/api/payments/webhook` runs over HTTPS in production.
- [x] Request payload body is read in raw byte format prior to JSON parsing to prevent whitespace signature corruption.
- [x] Signatures are compared using constant-time `hmac.compare_digest`.
- [x] Duplicate webhooks are logged and idempotently acknowledged with HTTP 200 without double-crediting orders.
- [x] Client amounts are strictly ignored—the payment status is verified against the database order record.
