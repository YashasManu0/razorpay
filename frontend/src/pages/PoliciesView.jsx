import React, { useState, useEffect } from "react";
import { Settings, ShieldCheck, Save, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { fetchPolicy, updatePolicy } from "../api";

function SliderRow({ label, desc, field, value, min, max, step, unit, prefix = "", onChange, accentColor }) {
  const numVal = parseFloat(value) || 0;
  const pct = Math.max(0, Math.min(100, Math.round(((numVal - min) / (max - min)) * 100)));

  return (
    <div className="glass rounded-2xl p-4 space-y-3" style={{border:"1px solid rgba(12,131,253,0.18)"}}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold text-white">{label}</div>
          <div className="text-[11px] text-slate-400 mt-0.5">{desc}</div>
        </div>
        <div className="text-lg font-extrabold font-mono" style={{color: accentColor, textShadow:`0 0 12px ${accentColor}80`}}>
          {prefix}{numVal.toLocaleString("en-IN")}{unit}
        </div>
      </div>
      <div className="relative h-2 rounded-full overflow-hidden" style={{background:"rgba(255,255,255,0.08)"}}>
        <div className="absolute left-0 top-0 h-full rounded-full transition-all" style={{width:`${pct}%`,background:`linear-gradient(90deg, ${accentColor}aa, ${accentColor})`}} />
        <input type="range" min={min} max={max} step={step} value={numVal}
          onChange={e => onChange(field, parseFloat(e.target.value))}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
      </div>
      <div className="flex justify-between text-[10px] text-slate-500 font-mono">
        <span>{prefix}{min.toLocaleString("en-IN")}{unit}</span>
        <span>{prefix}{max.toLocaleString("en-IN")}{unit}</span>
      </div>
    </div>
  );
}

function Toggle({ label, desc, field, value, onChange }) {
  return (
    <div className="glass rounded-2xl p-4 flex items-center justify-between gap-4" style={{border:"1px solid rgba(12,131,253,0.18)"}}>
      <div>
        <div className="text-sm font-semibold text-white">{label}</div>
        <div className="text-[11px] text-slate-400 mt-0.5">{desc}</div>
      </div>
      <button onClick={() => onChange(field, !value)}
        className="relative w-11 h-6 rounded-full transition-all shrink-0 cursor-pointer"
        style={{
          background: value ? "rgba(0,186,116,0.30)" : "rgba(255,255,255,0.08)",
          border: value ? "1px solid rgba(0,186,116,0.50)" : "1px solid rgba(255,255,255,0.12)",
          boxShadow: value ? "0 0 12px rgba(0,186,116,0.30)" : "none",
        }}
      >
        <div className="absolute top-0.5 h-5 w-5 rounded-full transition-all" style={{
          left: value ? "calc(100% - 22px)" : "2px",
          background: value ? "#00BA74" : "rgba(255,255,255,0.30)",
          boxShadow: value ? "0 0 8px rgba(0,186,116,0.60)" : "none",
        }} />
      </button>
    </div>
  );
}

export default function PoliciesView() {
  const [policy, setPolicy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { loadPolicy(); }, []);

  async function loadPolicy() {
    try {
      setLoading(true);
      const res = await fetchPolicy();
      setPolicy(res);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  async function handleSave() {
    setSaving(true); setError(null);
    try {
      const res = await updatePolicy(policy.id, {
        min_margin: parseFloat(policy.min_margin),
        max_discount_pct: parseFloat(policy.max_discount_pct),
        max_negotiation_rounds: parseInt(policy.max_negotiation_rounds),
        low_stock_threshold: parseInt(policy.low_stock_threshold),
        low_stock_max_discount: parseFloat(policy.low_stock_max_discount),
        aging_threshold_days: parseInt(policy.aging_threshold_days),
        aging_clearance_discount_boost: parseFloat(policy.aging_clearance_discount_boost),
        allow_free_shipping: policy.allow_free_shipping,
        allow_warranty_bundle: policy.allow_warranty_bundle,
        allow_accessory_bundle: policy.allow_accessory_bundle,
      });
      setPolicy(prev => ({ ...prev, version: res.policy.version }));
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) { setError(err.message); } finally { setSaving(false); }
  }

  function handleChange(field, val) {
    setPolicy(prev => ({ ...prev, [field]: val }));
  }

  if (loading) return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{borderColor:"rgba(12,131,253,0.3)",borderTopColor:"#0C83FD"}} />
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">

      <div className="flex flex-wrap items-center justify-between gap-4 pb-5" style={{borderBottom:"1px solid rgba(12,131,253,0.18)"}}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center" style={{background:"rgba(12,131,253,0.15)",border:"1px solid rgba(12,131,253,0.35)",boxShadow:"0 0 16px rgba(12,131,253,0.20)"}}>
            <Settings className="w-6 h-6 text-sky-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Merchant Negotiation Policy</h1>
            <p className="text-xs text-slate-400">Version {policy?.version || 1} — Controls AI pricing rules engine &amp; guardrails</p>
          </div>
        </div>
        <button onClick={handleSave} disabled={saving}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white disabled:opacity-50 transition-all cursor-pointer"
          style={{background:"#0C83FD",border:"1px solid rgba(12,131,253,0.40)",boxShadow:"0 0 20px rgba(12,131,253,0.35)"}}
          onMouseEnter={e => e.currentTarget.style.background="#0273E8"}
          onMouseLeave={e => e.currentTarget.style.background="#0C83FD"}
        >
          {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : savedSuccess ? <CheckCircle2 className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          <span>{saving ? "Saving..." : savedSuccess ? "Saved!" : "Save Policy"}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl flex items-center gap-2 text-rose-300 text-xs" style={{background:"rgba(251,113,133,0.12)",border:"1px solid rgba(251,113,133,0.30)"}}>
          <AlertCircle className="w-4 h-4" />{error}
        </div>
      )}

      {savedSuccess && (
        <div className="p-4 rounded-xl flex items-center gap-2 text-emerald-300 text-xs" style={{background:"rgba(0,186,116,0.12)",border:"1px solid rgba(0,186,116,0.30)"}}>
          <ShieldCheck className="w-4 h-4" />Policy updated and active. All future negotiations will follow new rules.
        </div>
      )}

      {policy && (
        <>
          <div>
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <span className="w-1.5 h-5 rounded-full bg-[#0C83FD]" style={{boxShadow:"0 0 8px rgba(12,131,253,0.6)"}} />
              Margin &amp; Discount Controls
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <SliderRow label="Minimum Profit Margin Floor" desc="AI will never offer a price yielding margin below this floor" field="min_margin" value={policy.min_margin} min={1000} max={15000} step={500} prefix="₹" unit="" onChange={handleChange} accentColor="#0C83FD" />
              <SliderRow label="Max Discount Cap" desc="Hard ceiling on any buyer discount" field="max_discount_pct" value={policy.max_discount_pct} min={1} max={25} step={0.5} unit="%" onChange={handleChange} accentColor="#6851FF" />
              <SliderRow label="Max Negotiation Rounds" desc="Per session round limit before auto-expire" field="max_negotiation_rounds" value={policy.max_negotiation_rounds} min={2} max={10} step={1} unit=" rds" onChange={handleChange} accentColor="#FF9900" />
            </div>
          </div>

          <div>
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <span className="w-1.5 h-5 rounded-full bg-amber-400" style={{boxShadow:"0 0 8px rgba(251,191,36,0.6)"}} />
              Inventory Protection Rules
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <SliderRow label="Low Stock Threshold" desc="Units at or below triggers scarcity guard" field="low_stock_threshold" value={policy.low_stock_threshold} min={1} max={20} step={1} unit=" units" onChange={handleChange} accentColor="#fbbf24" />
              <SliderRow label="Low-Stock Max Discount" desc="Max discount when scarcity guard is triggered" field="low_stock_max_discount" value={policy.low_stock_max_discount} min={0} max={5} step={0.5} unit="%" onChange={handleChange} accentColor="#fb7185" />
            </div>
          </div>

          <div>
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <span className="w-1.5 h-5 rounded-full bg-emerald-400" style={{boxShadow:"0 0 8px rgba(52,211,153,0.6)"}} />
              Aging Clearance Settings
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <SliderRow label="Aging Threshold (Days)" desc="Items older than this get clearance boost" field="aging_threshold_days" value={policy.aging_threshold_days} min={15} max={120} step={5} unit=" days" onChange={handleChange} accentColor="#00BA74" />
              <SliderRow label="Clearance Discount Boost" desc="Extra % added to aging items discount" field="aging_clearance_discount_boost" value={policy.aging_clearance_discount_boost} min={0} max={10} step={0.5} unit="%" onChange={handleChange} accentColor="#00BAF2" />
            </div>
          </div>

          <div>
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <span className="w-1.5 h-5 rounded-full bg-indigo-400" style={{boxShadow:"0 0 8px rgba(129,140,248,0.6)"}} />
              Bundle &amp; Perks Authorization
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Toggle label="Free Shipping" desc="Allow AI to offer free express delivery" field="allow_free_shipping" value={policy.allow_free_shipping} onChange={handleChange} />
              <Toggle label="Extended Warranty" desc="Allow AI to bundle extra warranty months" field="allow_warranty_bundle" value={policy.allow_warranty_bundle} onChange={handleChange} />
              <Toggle label="Accessory Bundle" desc="Allow AI to bundle complementary accessories" field="allow_accessory_bundle" value={policy.allow_accessory_bundle} onChange={handleChange} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
