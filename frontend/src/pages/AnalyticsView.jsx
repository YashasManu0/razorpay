import React, { useState, useEffect } from "react";
import { BarChart3, TrendingUp, ArrowUpRight } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from "recharts";
import { fetchAnalytics } from "../api";

const NEON_COLORS = ["#38bdf8","#34d399","#818cf8","#fbbf24","#fb7185","#a78bfa","#22d3ee"];

const GlassTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-strong rounded-xl p-3 text-xs space-y-1" style={{minWidth:140}}>
      <div className="font-semibold text-white mb-1">{label}</div>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{background:p.fill || p.color}} />
          <span className="text-slate-400">{p.name}:</span>
          <span className="font-mono font-bold text-white">Rs {Number(p.value).toLocaleString("en-IN")}</span>
        </div>
      ))}
    </div>
  );
};

export default function AnalyticsView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics().then(res => setData(res)).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading || !data) return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{borderColor:"rgba(99,102,241,0.3)",borderTopColor:"#818cf8"}} />
    </div>
  );

  const comp = data.comparison;
  const comparisonChartData = [
    { name:"Est. Revenue", Baseline: comp.baseline.est_revenue, AINegotiator: comp.ai_negotiator.est_revenue },
    { name:"Est. Profit",  Baseline: comp.baseline.est_profit,  AINegotiator: comp.ai_negotiator.est_profit },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5" style={{borderBottom:"1px solid rgba(255,255,255,0.08)"}}>
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-indigo-400" />Economic Impact & Policy Enforcement Analytics
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">Baseline (Fixed List Price) vs AI Negotiator Expected Profit Maximizer</p>
        </div>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full" style={{background:"rgba(52,211,153,0.12)",border:"1px solid rgba(52,211,153,0.30)",color:"#34d399"}}>
          <ArrowUpRight className="w-4 h-4" />
          <span className="text-xs font-bold">+{data.summary.profit_lift_pct}% Realized Profit Lift</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {[
          { label:"Conversion Rate Lift", main:`${comp.ai_negotiator.conversion_rate}%`, cmp:`vs ${comp.baseline.conversion_rate}% baseline`, lift:`+${data.summary.conversion_lift_pct}% higher transaction closure`, color:"rgba(52,211,153,", c:"text-emerald-400" },
          { label:"Revenue Uplift (Est.)", main:`Rs ${comp.ai_negotiator.est_revenue?.toLocaleString("en-IN")}`, cmp:`vs Rs ${comp.baseline.est_revenue?.toLocaleString("en-IN")} baseline`, lift:`+Rs ${(comp.ai_negotiator.est_revenue - comp.baseline.est_revenue)?.toLocaleString("en-IN")} incremental`, color:"rgba(56,189,248,", c:"text-sky-400" },
          { label:"Profit Lift (Est.)", main:`Rs ${comp.ai_negotiator.est_profit?.toLocaleString("en-IN")}`, cmp:`vs Rs ${comp.baseline.est_profit?.toLocaleString("en-IN")} baseline`, lift:`+${data.summary.profit_lift_pct}% expected lift`, color:"rgba(167,139,250,", c:"text-violet-400" },
        ].map(({ label, main, cmp, lift, color, c }) => (
          <div key={label} className="glass rounded-2xl p-6 space-y-3" style={{boxShadow:`0 0 24px ${color}0.10)`}}>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
            <div className="text-3xl font-extrabold text-white">{main}</div>
            <div className="text-xs text-slate-500">{cmp}</div>
            <div className={`text-xs font-semibold flex items-center gap-1 ${c}`}>
              <TrendingUp className="w-3.5 h-3.5" />{lift}
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Chart */}
      <div className="glass rounded-2xl p-6 space-y-4">
        <h2 className="text-sm font-bold text-white">Baseline vs AI Negotiator — Revenue & Profit</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={comparisonChartData} barCategoryGap="35%">
            <XAxis dataKey="name" tick={{fill:"#94a3b8",fontSize:11}} axisLine={false} tickLine={false} />
            <YAxis tick={{fill:"#64748b",fontSize:10}} axisLine={false} tickLine={false} tickFormatter={v=>`Rs ${(v/1000).toFixed(0)}k`} />
            <Tooltip content={<GlassTooltip />} cursor={{fill:"rgba(255,255,255,0.04)"}} />
            <Bar dataKey="Baseline" fill="#334155" radius={[6,6,0,0]} />
            <Bar dataKey="AINegotiator" radius={[6,6,0,0]}>
              {comparisonChartData.map((_, i) => <Cell key={i} fill={NEON_COLORS[i]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Category breakdown */}
      {data.by_category && (
        <div className="glass rounded-2xl p-6 space-y-4">
          <h2 className="text-sm font-bold text-white">Revenue by Category</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.by_category} layout="vertical" barCategoryGap="30%">
              <XAxis type="number" tick={{fill:"#64748b",fontSize:10}} axisLine={false} tickLine={false} tickFormatter={v=>`Rs ${(v/1000).toFixed(0)}k`} />
              <YAxis type="category" dataKey="category" tick={{fill:"#94a3b8",fontSize:11}} axisLine={false} tickLine={false} width={90} />
              <Tooltip content={<GlassTooltip />} cursor={{fill:"rgba(255,255,255,0.04)"}} />
              <Bar dataKey="revenue" radius={[0,6,6,0]}>
                {(data.by_category || []).map((_, i) => <Cell key={i} fill={NEON_COLORS[i % NEON_COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Discount distribution pie */}
      {data.discount_distribution && (
        <div className="glass rounded-2xl p-6 space-y-4">
          <h2 className="text-sm font-bold text-white">Discount Bracket Distribution</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={data.discount_distribution} dataKey="count" nameKey="bracket" cx="50%" cy="50%" outerRadius={80} paddingAngle={3}>
                {(data.discount_distribution || []).map((_, i) => <Cell key={i} fill={NEON_COLORS[i % NEON_COLORS.length]} />)}
              </Pie>
              <Tooltip content={<GlassTooltip />} />
              <Legend formatter={val=><span style={{color:"#94a3b8",fontSize:11}}>{val}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
