import React, { useState, useEffect } from "react";
import { X, ShieldAlert, CheckCircle2, AlertTriangle, Play, RefreshCw } from "lucide-react";
import { fetchFailureScenarios, triggerFailureScenario } from "../api";

export default function FailureInjectionModal({ isOpen, onClose, activeNegotiationId, activeOrderId }) {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (isOpen) { loadScenarios(); setResult(null); }
  }, [isOpen]);

  async function loadScenarios() {
    try {
      const data = await fetchFailureScenarios();
      setScenarios(data);
      if (data.length > 0 && !selectedScenario) setSelectedScenario(data[0]);
    } catch (e) { console.error(e); }
  }

  async function handleTrigger() {
    if (!selectedScenario) return;
    setLoading(true); setResult(null);
    try {
      const payload = { scenario_id: selectedScenario.id };
      if (activeNegotiationId) payload.negotiation_id = activeNegotiationId;
      if (activeOrderId) payload.order_id = activeOrderId;
      const res = await triggerFailureScenario(payload);
      setResult(res);
    } catch (e) { setResult({ error: e.message }); } finally { setLoading(false); }
  }

  if (!isOpen) return null;

  const severityStyle = (sev) => {
    if (sev === "HIGH" || sev === "CRITICAL") return { bg:"rgba(251,113,133,0.12)", border:"rgba(251,113,133,0.40)", color:"#fda4af", glow:"rgba(251,113,133,0.20)" };
    if (sev === "MEDIUM") return { bg:"rgba(251,191,36,0.12)", border:"rgba(251,191,36,0.40)", color:"#fbbf24", glow:"rgba(251,191,36,0.20)" };
    return { bg:"rgba(56,189,248,0.10)", border:"rgba(56,189,248,0.30)", color:"#7dd3fc", glow:"rgba(56,189,248,0.12)" };
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{background:"rgba(6,9,20,0.85)",backdropFilter:"blur(12px)"}}>
      <div className="w-full max-w-2xl glass-strong rounded-3xl overflow-hidden" style={{
        border:"1px solid rgba(251,113,133,0.30)",
        boxShadow:"0 0 60px rgba(251,113,133,0.12), 0 32px 80px rgba(0,0,0,0.7)",
        maxHeight:"90vh", display:"flex", flexDirection:"column",
      }}>
        {/* Header */}
        <div className="flex items-center justify-between p-5" style={{borderBottom:"1px solid rgba(255,255,255,0.08)"}}>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{background:"rgba(251,113,133,0.15)",border:"1px solid rgba(251,113,133,0.40)",boxShadow:"0 0 16px rgba(251,113,133,0.25)"}}>
              <ShieldAlert className="w-5 h-5 text-rose-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">BREAK THE AGENT</h2>
              <p className="text-[11px] text-slate-500">Inject failure scenarios to test system resilience</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-white transition-colors"
            style={{background:"rgba(255,255,255,0.05)",border:"1px solid rgba(255,255,255,0.10)"}}
          ><X className="w-4 h-4" /></button>
        </div>

        <div className="overflow-y-auto flex-1">
          {/* Scenario selection */}
          <div className="p-5 space-y-3">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Choose Failure Scenario:</div>
            <div className="space-y-2">
              {scenarios.map(sc => {
                const st = severityStyle(sc.severity);
                const isSelected = selectedScenario?.id === sc.id;
                return (
                  <button key={sc.id} onClick={() => setSelectedScenario(sc)}
                    className="w-full text-left p-4 rounded-2xl transition-all"
                    style={{
                      background: isSelected ? st.bg : "rgba(255,255,255,0.04)",
                      border: isSelected ? `1px solid ${st.border}` : "1px solid rgba(255,255,255,0.08)",
                      boxShadow: isSelected ? `0 0 16px ${st.glow}` : "none",
                    }}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-semibold text-white">{sc.name}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase" style={{background:st.bg,border:`1px solid ${st.border}`,color:st.color}}>
                        {sc.severity}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">{sc.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Context info */}
          {(activeNegotiationId || activeOrderId) && (
            <div className="px-5 pb-3">
              <div className="p-3 rounded-xl text-xs space-y-1" style={{background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.08)"}}>
                <div className="font-semibold text-slate-400 uppercase tracking-wider text-[10px]">Will target:</div>
                {activeNegotiationId && <div className="font-mono text-sky-400">Negotiation: {activeNegotiationId.slice(0,16)}...</div>}
                {activeOrderId && <div className="font-mono text-violet-400">Order: {activeOrderId.slice(0,16)}...</div>}
              </div>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className="px-5 pb-4">
              {result.error ? (
                <div className="p-4 rounded-xl flex items-start gap-3 text-xs" style={{background:"rgba(251,113,133,0.10)",border:"1px solid rgba(251,113,133,0.30)"}}>
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <div className="font-mono text-rose-300">{result.error}</div>
                </div>
              ) : (
                <div className="p-4 rounded-xl space-y-2" style={{background:"rgba(52,211,153,0.08)",border:"1px solid rgba(52,211,153,0.25)"}}>
                  <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                    <CheckCircle2 className="w-4 h-4" />Scenario triggered successfully
                  </div>
                  <pre className="text-[11px] font-mono text-slate-400 overflow-x-auto whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-5 flex items-center justify-between" style={{borderTop:"1px solid rgba(255,255,255,0.08)"}}>
          <button onClick={onClose} className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white transition-colors"
            style={{background:"rgba(255,255,255,0.05)",border:"1px solid rgba(255,255,255,0.10)"}}>Cancel</button>
          <button onClick={handleTrigger} disabled={loading || !selectedScenario}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white disabled:opacity-40 transition-all"
            style={{background:"linear-gradient(135deg,#dc2626,#9f1239)",border:"1px solid rgba(251,113,133,0.40)",boxShadow:"0 0 24px rgba(251,113,133,0.25)"}}
            onMouseEnter={e => e.currentTarget.style.boxShadow="0 0 32px rgba(251,113,133,0.45)"}
            onMouseLeave={e => e.currentTarget.style.boxShadow="0 0 24px rgba(251,113,133,0.25)"}
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            <span>{loading ? "Injecting Failure..." : "Trigger Failure Scenario"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
