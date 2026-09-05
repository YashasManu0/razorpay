import React, { useState, useEffect } from "react";
import { HelpCircle, ShieldCheck, Layers, FileText } from "lucide-react";
import { fetchOfferExplanation, fetchAuditLogs, listNegotiations } from "../api";

export default function AuditView({ selectedOfferId }) {
  const [offerId, setOfferId] = useState(selectedOfferId || "");
  const [explanation, setExplanation] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { loadRecentNegotiationOffer(); loadLogs(); }, []);
  useEffect(() => { if (selectedOfferId) { setOfferId(selectedOfferId); loadExplanation(selectedOfferId); } }, [selectedOfferId]);

  async function loadRecentNegotiationOffer() {
    if (offerId) return;
    try {
      const negs = await listNegotiations({ limit: 10 });
      const withOffer = negs.find(n => n.active_offer_price !== null);
      if (withOffer) {
        const detRes = await fetch(`/api/negotiations/${withOffer.id}`);
        const det = await detRes.json();
        if (det.active_offer?.id) { setOfferId(det.active_offer.id); loadExplanation(det.active_offer.id); }
      }
    } catch (e) { console.error(e); }
  }

  async function loadExplanation(idToLoad) {
    if (!idToLoad) return;
    setLoading(true); setError(null);
    try { const res = await fetchOfferExplanation(idToLoad); setExplanation(res); }
    catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  async function loadLogs() {
    try { const res = await fetchAuditLogs(); setLogs(res || []); } catch (e) { console.error(e); }
  }

  const summary = explanation?.summary;
  const stepColors = ["rgba(56,189,248,","rgba(52,211,153,","rgba(167,139,250,","rgba(251,191,36,","rgba(251,113,133,","rgba(34,211,238,"];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5" style={{borderBottom:"1px solid rgba(255,255,255,0.08)"}}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center" style={{background:"rgba(167,139,250,0.15)",border:"1px solid rgba(167,139,250,0.35)",boxShadow:"0 0 16px rgba(167,139,250,0.20)"}}>
            <HelpCircle className="w-6 h-6 text-violet-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">"WHY DID THE AI OFFER THIS PRICE?"</h1>
            <p className="text-xs text-slate-500">Deterministic Mathematical & Policy Audit Trail Inspector</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <input type="text" value={offerId} onChange={e => setOfferId(e.target.value)}
            placeholder="Enter Offer UUID..." className="input-glass rounded-xl px-3 py-1.5 text-xs font-mono w-60"
          />
          <button onClick={() => loadExplanation(offerId)}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold text-white transition-all"
            style={{background:"rgba(167,139,250,0.20)",border:"1px solid rgba(167,139,250,0.40)"}}
            onMouseEnter={e => e.currentTarget.style.boxShadow="0 0 16px rgba(167,139,250,0.35)"}
            onMouseLeave={e => e.currentTarget.style.boxShadow="none"}
          >Audit</button>
        </div>
      </div>

      {error && <div className="p-4 rounded-xl text-rose-300 text-xs" style={{background:"rgba(251,113,133,0.10)",border:"1px solid rgba(251,113,133,0.30)"}}>{error}</div>}

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{borderColor:"rgba(167,139,250,0.3)",borderTopColor:"#a78bfa"}} />
        </div>
      )}

      {summary && !loading && (
        <div className="glass-strong rounded-2xl p-6 space-y-4" style={{border:"1px solid rgba(167,139,250,0.30)",boxShadow:"0 0 40px rgba(167,139,250,0.08)"}}>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <span className="text-slate-500 uppercase tracking-wider text-[10px]">Product Audited</span>
              <h2 className="text-lg font-bold text-white">{summary.product_title}</h2>
            </div>
            <div className="text-right">
              <span className="text-slate-500 uppercase tracking-wider text-[10px]">Authorized Price</span>
              <div className="text-2xl font-extrabold text-violet-400" style={{textShadow:"0 0 20px rgba(167,139,250,0.5)"}}>
                Rs {summary.final_offer_price?.toLocaleString("en-IN")}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4" style={{borderTop:"1px solid rgba(255,255,255,0.08)"}}>
            {[
              ["List Price", `Rs ${summary.list_price?.toLocaleString("en-IN")}`, "text-white"],
              ["Unit Cost", `Rs ${summary.merchant_cost?.toLocaleString("en-IN")}`, "font-mono text-slate-300"],
              ["Realized Margin", `Rs ${summary.merchant_margin?.toLocaleString("en-IN")}`, "font-mono text-emerald-400"],
              ["Expected Profit", `Rs ${summary.expected_profit?.toLocaleString("en-IN")}`, "font-mono text-sky-400"],
            ].map(([label, val, cls]) => (
              <div key={label} className="p-3 rounded-xl" style={{background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.08)"}}>
                <span className="text-[10px] text-slate-500 block mb-1">{label}</span>
                <div className={`font-bold ${cls}`}>{val}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {explanation?.decision_chain_steps && !loading && (
        <div className="space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-violet-400" />End-to-End Decision Chain Flow
          </h2>
          <div className="space-y-4 relative">
            <div className="absolute left-[22px] top-0 bottom-0 w-px pointer-events-none" style={{background:"linear-gradient(to bottom,rgba(167,139,250,0.40),rgba(56,189,248,0.20),transparent)"}} />
            {explanation.decision_chain_steps.map((step, i) => {
              const col = stepColors[i % stepColors.length];
              return (
                <div key={step.step_number} className="relative z-10 flex items-start gap-4 glass rounded-2xl p-5">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm shrink-0 text-white" style={{
                    background:`${col}0.15)`, border:`1px solid ${col}0.40)`, boxShadow:`0 0 12px ${col}0.20)`,
                  }}>
                    {step.step_number}
                  </div>
                  <div className="flex-1 space-y-2">
                    <h3 className="text-sm font-bold text-white">{step.title}</h3>
                    <p className="text-xs text-slate-400">{step.description}</p>
                    <div className="p-3 rounded-xl font-mono text-[11px] text-slate-300 overflow-x-auto" style={{background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.08)"}}>
                      <pre>{JSON.stringify(step.details, null, 2)}</pre>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="space-y-4 pt-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <FileText className="w-5 h-5 text-sky-400" />Immutable Audit Ledger Logs
        </h2>
        <div className="glass rounded-2xl overflow-hidden">
          <table className="w-full text-left table-glass">
            <thead><tr>{["Timestamp","Entity","Action","Actor","Details"].map(h=><th key={h}>{h}</th>)}</tr></thead>
            <tbody>
              {logs.slice(0,15).map(l => (
                <tr key={l.id}>
                  <td className="font-mono text-slate-500 text-[11px]">{new Date(l.timestamp).toLocaleTimeString()}</td>
                  <td className="font-mono text-slate-400 capitalize">{l.entity_type}</td>
                  <td className="font-semibold text-white">{l.action}</td>
                  <td className="text-sky-400 font-mono text-[11px]">{l.actor}</td>
                  <td className="font-mono text-[10px] text-slate-500 max-w-xs truncate">{JSON.stringify(l.details)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
