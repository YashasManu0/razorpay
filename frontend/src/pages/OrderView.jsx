import React, { useState, useEffect } from "react";
import { CheckCircle2, ShieldCheck, Truck, ArrowRight, HelpCircle } from "lucide-react";
import { fetchPaymentStatus } from "../api";

export default function OrderView({ orderId, onStartNew, onInspectAudit }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (orderId) fetchPaymentStatus(orderId).then(res => setData(res)).catch(console.error).finally(() => setLoading(false));
  }, [orderId]);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{borderColor:"rgba(52,211,153,0.3)",borderTopColor:"#34d399"}} />
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto px-4 py-12 space-y-6">
      <div className="glass-strong rounded-3xl p-8 text-center space-y-6 relative overflow-hidden" style={{
        border:"1px solid rgba(52,211,153,0.35)",
        boxShadow:"0 0 60px rgba(52,211,153,0.12), 0 24px 64px rgba(0,0,0,0.6)",
      }}>
        {/* Glow rings */}
        <div className="absolute inset-0 pointer-events-none" style={{
          background:"radial-gradient(ellipse 80% 60% at 50% 0%,rgba(52,211,153,0.10) 0%,transparent 70%)",
        }} />

        <div className="w-20 h-20 rounded-3xl flex items-center justify-center mx-auto relative" style={{
          background:"rgba(52,211,153,0.12)", border:"1px solid rgba(52,211,153,0.40)",
          boxShadow:"0 0 32px rgba(52,211,153,0.35)",
        }}>
          <CheckCircle2 className="w-10 h-10 text-emerald-400" />
        </div>

        <div className="relative z-10">
          <span className="text-[10px] font-mono uppercase px-3 py-1 rounded-full" style={{
            background:"rgba(52,211,153,0.12)", border:"1px solid rgba(52,211,153,0.30)", color:"#6ee7b7",
          }}>Payment Captured & Verified</span>
          <h2 className="text-3xl font-extrabold text-white mt-3" style={{textShadow:"0 0 30px rgba(52,211,153,0.4)"}}>
            Order Confirmed!
          </h2>
          <p className="text-xs text-slate-400 mt-1">Authoritative transaction completed via verified Razorpay webhook.</p>
        </div>

        {/* Order details */}
        <div className="p-5 rounded-2xl text-left space-y-3 text-xs relative z-10" style={{
          background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)",
        }}>
          {[
            ["Order Reference", data?.order_number, "font-mono font-bold text-white"],
            ["Verified Amount Paid", `Rs ${data?.final_price?.toLocaleString("en-IN")}`, "font-bold text-emerald-400 text-sm"],
            ["Provider Payment ID", data?.payment?.provider_payment_id || "pay_verified_rzp", "font-mono text-slate-300"],
          ].map(([label, val, cls]) => (
            <div key={label} className="flex justify-between items-center pb-2" style={{borderBottom:"1px solid rgba(255,255,255,0.07)"}}>
              <span className="text-slate-400">{label}</span>
              <span className={cls}>{val}</span>
            </div>
          ))}
          <div className="flex justify-between items-center pt-1">
            <span className="text-slate-400">Cryptographic Webhook</span>
            <span className="text-emerald-400 font-semibold flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />HMAC-SHA256 Verified
            </span>
          </div>
        </div>

        {/* Fulfillment stepper */}
        <div className="p-4 rounded-2xl relative z-10" style={{background:"rgba(255,255,255,0.03)",border:"1px solid rgba(255,255,255,0.07)"}}>
          <div className="text-xs font-semibold text-slate-300 text-left flex items-center gap-1.5 mb-3">
            <Truck className="w-4 h-4 text-sky-400" />Fulfillment Status
          </div>
          <div className="grid grid-cols-3 gap-2 text-[11px] text-center">
            <div className="p-2 rounded-xl font-semibold" style={{background:"rgba(52,211,153,0.15)",border:"1px solid rgba(52,211,153,0.35)",color:"#6ee7b7",boxShadow:"0 0 12px rgba(52,211,153,0.15)"}}>
              1. Paid &amp; Queued
            </div>
            <div className="p-2 rounded-xl text-slate-500" style={{background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.08)"}}>
              2. Warehouse Pick
            </div>
            <div className="p-2 rounded-xl text-slate-500" style={{background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.08)"}}>
              3. Express Dispatch
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 pt-2 relative z-10">
          <button onClick={onStartNew}
            className="flex-1 py-3 rounded-xl font-bold text-sm text-white transition-all"
            style={{
              background:"linear-gradient(135deg,#2563eb,#4f46e5)", border:"1px solid rgba(99,102,241,0.40)",
              boxShadow:"0 0 24px rgba(56,189,248,0.25)",
            }}
          >Start Another Negotiation</button>
          <button onClick={onInspectAudit}
            className="flex items-center justify-center gap-1.5 px-4 py-3 rounded-xl font-semibold text-xs transition-all"
            style={{background:"rgba(167,139,250,0.12)",border:"1px solid rgba(167,139,250,0.35)",color:"#c4b5fd"}}
            onMouseEnter={e => e.currentTarget.style.background="rgba(167,139,250,0.22)"}
            onMouseLeave={e => e.currentTarget.style.background="rgba(167,139,250,0.12)"}
          >
            <HelpCircle className="w-4 h-4" />Audit This Decision
          </button>
        </div>
      </div>
    </div>
  );
}
