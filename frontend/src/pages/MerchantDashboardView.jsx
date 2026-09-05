import React, { useState, useEffect } from "react";
import { Store, TrendingUp, DollarSign, Percent, Activity, AlertTriangle, Clock, ArrowRight } from "lucide-react";
import { fetchMerchants, fetchMerchantDashboard, listNegotiations } from "../api";

export default function MerchantDashboardView({ setView, onSelectNegotiation }) {
  const [merchants, setMerchants] = useState([]);
  const [selectedMerchantId, setSelectedMerchantId] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [negotiations, setNegotiations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadMerchants(); }, []);
  useEffect(() => { if (selectedMerchantId) loadDashboard(selectedMerchantId); }, [selectedMerchantId]);

  async function loadMerchants() {
    try { setLoading(true); const data = await fetchMerchants(); setMerchants(data); if (data.length > 0) setSelectedMerchantId(data[0].id); }
    catch (e) { console.error(e); } finally { setLoading(false); }
  }
  async function loadDashboard(mId) {
    try {
      const [dash, negs] = await Promise.all([fetchMerchantDashboard(mId), listNegotiations({ merchant_id: mId, limit: 8 })]);
      setDashboard(dash); setNegotiations(negs);
    } catch (e) { console.error(e); }
  }

  const kpis = dashboard?.kpis;

  const kpiCards = [
    { label:"Realized Revenue", value:`₹${kpis?.total_revenue?.toLocaleString("en-IN") || 0}`, sub:`${kpis?.paid_orders || 0} Paid Settlements`, icon: DollarSign, color:"#0C83FD" },
    { label:"Realized Net Margin", value:`₹${kpis?.total_profit?.toLocaleString("en-IN") || 0}`, sub:`Avg Margin: ${kpis?.avg_margin_pct || 22.5}%`, icon: TrendingUp, color:"#00BA74", valColor:"#00BA74" },
    { label:"Agent Conversion Rate", value:`${kpis?.conversion_rate || 42.0}%`, sub:"+23.5% vs Fixed Price Baseline", icon: Percent, color:"#00BAF2", subColor:"text-emerald-400" },
    { label:"Active Agent Sessions", value:kpis?.active_negotiations || 0, sub:`Across ${kpis?.total_products || 107} live SKUs`, icon: Activity, color:"#6851FF" },
  ];

  const statusStyle = (s) => {
    if (s === "COMPLETED" || s === "PAID") return { bg:"rgba(0,186,116,0.15)", border:"rgba(0,186,116,0.40)", color:"#6ee7b7" };
    if (s === "ACCEPTED") return { bg:"rgba(12,131,253,0.15)", border:"rgba(12,131,253,0.40)", color:"#7dd3fc" };
    if (s === "EXPIRED") return { bg:"rgba(251,113,133,0.15)", border:"rgba(251,113,133,0.40)", color:"#fda4af" };
    return { bg:"rgba(255,255,255,0.06)", border:"rgba(255,255,255,0.15)", color:"#94a3b8" };
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5" style={{borderBottom:"1px solid rgba(12,131,253,0.18)"}}>
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{background:"rgba(12,131,253,0.15)",border:"1px solid rgba(12,131,253,0.35)",boxShadow:"0 0 16px rgba(12,131,253,0.25)"}}>
            <Store className="w-6 h-6 text-sky-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">{dashboard?.merchant?.business_name || "Razorpay Merchant Cockpit"}</h1>
            <p className="text-xs text-slate-400">Autonomous Merchant-Side Commerce &amp; Real-Time Margin Optimization</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400">Merchant Store:</span>
          <select value={selectedMerchantId || ""} onChange={e => setSelectedMerchantId(e.target.value)}
            className="rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
            style={{background:"rgba(8,16,36,0.90)",border:"1px solid rgba(12,131,253,0.25)"}}>
            {merchants.map(m => <option key={m.id} value={m.id}>{m.business_name} ({m.product_count} items)</option>)}
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.map(({ label, value, sub, icon: Icon, color, valColor, subColor }) => (
          <div key={label} className="glass rounded-2xl p-5 space-y-2 hover:scale-[1.02] transition-transform" style={{
            border: `1px solid ${color}35`,
            boxShadow: `0 8px 24px rgba(2,4,43,0.6)`,
          }}>
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>{label}</span>
              <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{background:`${color}18`,border:`1px solid ${color}45`}}>
                <Icon className="w-4 h-4" style={{color}} />
              </div>
            </div>
            <div className="text-2xl font-extrabold" style={{color: valColor || "white"}}>{value}</div>
            <div className={`text-[11px] ${subColor || "text-slate-400"}`}>{sub}</div>
          </div>
        ))}
      </div>

      {/* Razorpay Guardrail Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-2xl flex items-center justify-between glass" style={{border:"1px solid rgba(255,153,0,0.30)",background:"rgba(255,153,0,0.06)"}}>
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <div>
              <div className="text-xs font-bold text-white">Low Stock Scarcity Guard Active</div>
              <div className="text-[11px] text-slate-400">{kpis?.low_stock_alerts || 4} items &le; 5 units. Max discount capped at 2.0%.</div>
            </div>
          </div>
          <button onClick={() => setView("inventory")} className="text-xs px-3 py-1.5 rounded-lg shrink-0 transition-all font-semibold cursor-pointer"
            style={{background:"rgba(255,153,0,0.15)",border:"1px solid rgba(255,153,0,0.35)",color:"#fbbf24"}}
          >Review</button>
        </div>
        <div className="p-4 rounded-2xl flex items-center justify-between glass" style={{border:"1px solid rgba(12,131,253,0.30)",background:"rgba(12,131,253,0.06)"}}>
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-sky-400" />
            <div>
              <div className="text-xs font-bold text-white">Aging Warehouse Clearance Boost Active</div>
              <div className="text-[11px] text-slate-400">{kpis?.aging_inventory_alerts || 8} items aged &ge; 60 days. Clearance bonus (+3%) enabled.</div>
            </div>
          </div>
          <button onClick={() => setView("inventory")} className="text-xs px-3 py-1.5 rounded-lg shrink-0 transition-all font-semibold cursor-pointer"
            style={{background:"rgba(12,131,253,0.15)",border:"1px solid rgba(12,131,253,0.35)",color:"#7dd3fc"}}
          >Inspect</button>
        </div>
      </div>

      {/* Negotiations Ledger Table */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" />Razorpay Autonomous Settlement Ledger
          </h2>
          <span className="text-xs text-slate-400">Click any row to view transaction telemetry</span>
        </div>

        <div className="glass rounded-2xl overflow-hidden" style={{border:"1px solid rgba(12,131,253,0.20)",boxShadow:"0 16px 48px rgba(2,4,43,0.7)"}}>
          <table className="w-full text-left table-glass">
            <thead><tr>
              {["Session ID","Buyer Agent","Product","Current Offer","Expected Profit","Status","Actions"].map(h => <th key={h}>{h}</th>)}
            </tr></thead>
            <tbody>
              {negotiations.map(n => {
                const st = statusStyle(n.status);
                return (
                  <tr key={n.id} onClick={() => onSelectNegotiation(n.id)} className="cursor-pointer hover:bg-[#0C83FD]/10 transition-colors">
                    <td className="font-mono text-sky-300 font-semibold">{n.id.slice(0,8)}...</td>
                    <td className="font-medium text-white">{n.buyer_name}</td>
                    <td className="text-slate-300 max-w-[140px] truncate">{n.product_title}</td>
                    <td className="font-bold text-white">{n.active_offer_price ? `₹${n.active_offer_price.toLocaleString("en-IN")}` : "Evaluating..."}</td>
                    <td className="font-mono text-emerald-400 font-bold">{n.expected_profit ? `₹${n.expected_profit.toLocaleString("en-IN")}` : "--"}</td>
                    <td>
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase" style={{background:st.bg,border:`1px solid ${st.border}`,color:st.color}}>
                        {n.status}
                      </span>
                    </td>
                    <td className="text-right">
                      <button className="flex items-center gap-1 ml-auto text-sky-400 hover:text-sky-300 font-semibold text-xs transition-colors">
                        Inspect<ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
