import React, { useState, useEffect } from "react";
import { ShieldCheck, CheckCircle2, Lock, AlertTriangle, RefreshCw, QrCode } from "lucide-react";
import { createPaymentSession, fetchPaymentStatus, verifyClientPayment } from "../api";

export default function PaymentView({ orderId, onPaymentComplete }) {
  const [session, setSession] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { if (orderId) initSession(); }, [orderId]);

  async function initSession() {
    try {
      setLoading(true);
      const res = await createPaymentSession({ order_id: orderId });
      setSession(res);
      const st = await fetchPaymentStatus(orderId);
      setStatusData(st);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  async function handleLiveRazorpayCheckout() {
    setError(null);
    if (!window.Razorpay) {
      setError("Razorpay SDK not loaded. Please check your internet connection.");
      return;
    }

    try {
      const options = {
        key: session.key_id,
        amount: session.amount_paise,
        currency: session.currency || "INR",
        name: "AI Agent Negotiator",
        description: `Order ${statusData?.order_number || orderId?.slice(0,8)}`,
        order_id: session.provider_order_id,
        handler: async function (response) {
          setPaying(true);
          try {
            await verifyClientPayment({
              order_id: orderId,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature
            });
            const st = await fetchPaymentStatus(orderId);
            setStatusData(st);
            setTimeout(() => onPaymentComplete(orderId), 1200);
          } catch (err) {
            setError(err.message);
          } finally {
            setPaying(false);
          }
        },
        theme: {
          color: "#2563eb"
        }
      };

      const rzp = new window.Razorpay(options);
      rzp.on("payment.failed", function (response) {
        setError(response.error?.description || "Payment failed at gateway");
      });
      rzp.open();
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading && !session) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{borderColor:"rgba(56,189,248,0.3)",borderTopColor:"#38bdf8"}} />
        <p className="text-xs text-slate-400">Connecting to Razorpay Gateway...</p>
      </div>
    </div>
  );

  const isPaid = statusData?.order_status === "PAID" || statusData?.payment?.status === "CAPTURED";

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-6">

      {/* Security Banner */}
      <div className="p-4 rounded-2xl flex items-start gap-3" style={{
        background:"rgba(56,189,248,0.08)", border:"1px solid rgba(56,189,248,0.25)",
        boxShadow:"0 0 20px rgba(56,189,248,0.08)",
      }}>
        <ShieldCheck className="w-5 h-5 text-sky-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 leading-relaxed">
          <span className="font-bold text-white">Cryptographically Protected Transaction: </span>
          The payment amount is authoritative and dictated strictly by the merchant negotiation ledger. Client-side price tampering is rejected server-side with HMAC-SHA256 verification.
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">

        {/* Order Summary */}
        <div className="md:col-span-5">
          <div className="glass-strong rounded-2xl p-5 space-y-4">
            <div>
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">Order Reference</span>
              <h3 className="text-base font-bold text-white font-mono mt-0.5">{statusData?.order_number || orderId?.slice(0,8)}</h3>
            </div>

            <div className="pt-3 space-y-2 text-xs" style={{borderTop:"1px solid rgba(255,255,255,0.08)"}}>
              {[
                ["Authorized Price", `Rs ${statusData?.final_price?.toLocaleString("en-IN")}`, "text-white"],
                ["Shipping", "FREE (Authorized)", "text-emerald-400"],
                ["GST (Included)", "18%", "text-slate-300"],
              ].map(([label, val, cls]) => (
                <div key={label} className="flex justify-between text-slate-400">
                  <span>{label}</span><span className={`font-medium ${cls}`}>{val}</span>
                </div>
              ))}
              <div className="pt-3 flex justify-between items-baseline" style={{borderTop:"1px solid rgba(255,255,255,0.08)"}}>
                <span className="font-bold text-white text-sm">Total Due</span>
                <span className="text-2xl font-extrabold text-white" style={{textShadow:"0 0 20px rgba(56,189,248,0.4)"}}>
                  Rs {statusData?.final_price?.toLocaleString("en-IN")}
                </span>
              </div>
            </div>

            <div className="p-2.5 rounded-xl flex items-center gap-2 text-[11px] text-slate-400" style={{background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.08)"}}>
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>Inventory Reserved — 10:00 mins</span>
            </div>
          </div>
        </div>

        {/* Razorpay Panel */}
        <div className="md:col-span-7">
          <div className="glass-strong rounded-2xl p-6 space-y-5" style={{boxShadow:"0 0 40px rgba(0,0,0,0.5)"}}>

            <div className="flex items-center justify-between pb-4" style={{borderBottom:"1px solid rgba(255,255,255,0.08)"}}>
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg flex items-center justify-center text-white font-bold text-xs" style={{background:"linear-gradient(135deg,#2563eb,#4f46e5)"}}>R</div>
                <div>
                  <h4 className="text-sm font-bold text-white">Razorpay Payment Gateway</h4>
                  <p className="text-[10px] text-slate-500">Official Checkout with QR Code &amp; UPI</p>
                </div>
              </div>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-md font-semibold" style={{
                background: "rgba(52,211,153,0.15)",
                border: "1px solid rgba(52,211,153,0.35)",
                color: "#6ee7b7"
              }}>
                RAZORPAY GATEWAY
              </span>
            </div>

            {/* Gateway Order Details */}
            <div className="p-4 rounded-xl space-y-2 text-xs" style={{background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.08)"}}>
              <div className="flex justify-between items-center text-[11px] text-slate-400">
                <span>Gateway Key ID:</span>
                <span className="font-mono text-sky-300">{session?.key_id}</span>
              </div>
              <div className="flex justify-between items-center text-[11px] text-slate-400">
                <span>Gateway Order ID:</span>
                <span className="font-mono text-slate-300">{session?.provider_order_id}</span>
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-xl text-rose-300 text-xs flex items-center gap-2" style={{background:"rgba(251,113,133,0.10)",border:"1px solid rgba(251,113,133,0.30)"}}>
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" /><span>{error}</span>
              </div>
            )}

            {isPaid ? (
              <div className="p-4 rounded-xl text-emerald-300 text-xs flex items-center justify-center gap-2" style={{background:"rgba(52,211,153,0.10)",border:"1px solid rgba(52,211,153,0.30)"}}>
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span className="font-bold text-sm">Payment Verified &amp; Captured! Redirecting...</span>
              </div>
            ) : (
              <div className="space-y-3">
                <button
                  onClick={handleLiveRazorpayCheckout}
                  disabled={paying}
                  className="w-full py-4 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50 transition-all cursor-pointer"
                  style={{
                    background: "linear-gradient(135deg,#0284c7,#2563eb,#4f46e5)",
                    border: "1px solid rgba(56,189,248,0.50)",
                    color: "white",
                    boxShadow: "0 0 28px rgba(56,189,248,0.30)",
                  }}
                >
                  {paying ? (
                    <><RefreshCw className="w-4 h-4 animate-spin" /><span>Verifying Gateway Settlement...</span></>
                  ) : (
                    <>
                      <QrCode className="w-4 h-4 text-sky-200" />
                      <span>Pay Rs {statusData?.final_price?.toLocaleString("en-IN")} via Razorpay (QR / UPI / Cards)</span>
                    </>
                  )}
                </button>
              </div>
            )}

            <div className="text-center text-[10px] text-slate-500">
              Server-authoritative settlement — Cryptographic HMAC-SHA256 signature verification.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
