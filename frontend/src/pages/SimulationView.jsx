import React, { useState, useEffect } from "react";
import { Cpu, Play, RefreshCw, TrendingUp, Award, Zap } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { fetchSimulationState, runBanditSimulation } from "../api";

const GlassTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-strong rounded-xl p-3 text-xs">
      <div className="text-slate-400 mb-1">Trial {label}</div>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{background:p.stroke}} />
          <span className="font-mono font-bold text-white">Rs {Number(p.value).toLocaleString("en-IN")}</span>
        </div>
      ))}
    </div>
  );
};

export default function SimulationView() {
  const [state, setState] = useState(null);
  const [running, setRunning] = useState(false);
  const [lastResult, setLastResult] = useState(null);

  useEffect(() => { loadState(); }, []);

  async function loadState() {
    try { const res = await fetchSimulationState(); setState(res); } catch (e) { console.error(e); }
  }

  async function handleRun(nTrials, reset = false) {
    setRunning(true);
    try { const res = await runBanditSimulation(nTrials, reset); setLastResult(res); await loadState(); }
    catch (e) { console.error(e); } finally { setRunning(false); }
  }

  const history = state?.history || [];
  const chartData = history.map((h, i) => ({ trial: h.trial || i + 1, cumulativeProfit: h.cumulative_profit, profit: h.profit }));

  const actionTotals = {};
  history.forEach(h => { actionTotals[h.action] = (actionTotals[h.action] || 0) + 1; });
  const actionsSorted = Object.entries(actionTotals).sort((a,b) => b[1]-a[1]);

  const actionColors = { AGGRESSIVE:"#fb7185", MODERATE:"#fbbf24", CONSERVATIVE:"#34d399", CLEARANCE:"#38bdf8", NO_DEAL:"#94a3b8" };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5" style={{borderBottom:"1px solid rgba(255,255,255,0.08)"}}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center" style={{background:"rgba(251,191,36,0.15)",border:"1px solid rgba(251,191,36,0.35)",boxShadow:"0 0 16px rgba(251,191,36,0.20)"}}>
            <Cpu className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Contextual Bandit Online Learning Simulator</h1>
            <p className="text-xs text-slate-500">LinUCB Exploration-Exploitation Policy Learning over Repeated Autonomous Transactions</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">{state?.total_trials || 0} total trials</span>
          {state?.total_trials > 0 && (
            <span className="text-xs font-mono px-2 py-0.5 rounded-lg" style={{background:"rgba(52,211,153,0.12)",border:"1px solid rgba(52,211,153,0.30)",color:"#34d399"}}>
              Best: {state?.best_action || "--"}
            </span>
          )}
        </div>
      </div>

      {/* Run controls */}
      <div className="glass rounded-2xl p-5 flex flex-wrap items-center gap-3">
        <Zap className="w-5 h-5 text-amber-400" />
        <span className="text-sm font-semibold text-white">Run Simulation Trials:</span>
        {[10, 50, 100, 500].map(n => (
          <button key={n} onClick={() => handleRun(n)} disabled={running}
            className="px-4 py-2 rounded-xl text-sm font-bold text-white transition-all disabled:opacity-40"
            style={{background:"rgba(251,191,36,0.18)",border:"1px solid rgba(251,191,36,0.40)"}}
            onMouseEnter={e => { e.currentTarget.style.background="rgba(251,191,36,0.30)"; e.currentTarget.style.boxShadow="0 0 16px rgba(251,191,36,0.30)"; }}
            onMouseLeave={e => { e.currentTarget.style.background="rgba(251,191,36,0.18)"; e.currentTarget.style.boxShadow="none"; }}
          >
            {running ? <RefreshCw className="w-4 h-4 animate-spin mx-auto" /> : `+${n} Trials`}
          </button>
        ))}
        <button onClick={() => handleRun(10, true)} disabled={running}
          className="px-4 py-2 rounded-xl text-xs font-semibold transition-all disabled:opacity-40"
          style={{background:"rgba(251,113,133,0.12)",border:"1px solid rgba(251,113,133,0.30)",color:"#fda4af"}}
        >Reset & Run</button>
      </div>

      {/* Main stats */}
      {state && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label:"Total Trials", val: state.total_trials, color:"rgba(56,189,248," },
            { label:"Cumulative Profit", val:`Rs ${state.cumulative_profit?.toLocaleString("en-IN")}`, color:"rgba(52,211,153,", vc:"#34d399" },
            { label:"Avg Profit / Trial", val:`Rs ${state.avg_profit?.toLocaleString("en-IN")}`, color:"rgba(167,139,250,", vc:"#a78bfa" },
            { label:"Best Strategy", val: state.best_action || "--", color:"rgba(251,191,36,", vc:"#fbbf24" },
          ].map(({ label, val, color, vc }) => (
            <div key={label} className="glass rounded-2xl p-4 space-y-1" style={{boxShadow:`0 0 20px ${color}0.10)`}}>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider">{label}</div>
              <div className="text-lg font-extrabold" style={{color: vc || "white"}}>{val}</div>
            </div>
          ))}
        </div>
      )}

      {/* Cumulative profit chart */}
      {chartData.length > 0 && (
        <div className="glass rounded-2xl p-6 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />Cumulative Profit Trajectory
          </h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <XAxis dataKey="trial" tick={{fill:"#64748b",fontSize:10}} axisLine={false} tickLine={false} />
              <YAxis tick={{fill:"#64748b",fontSize:10}} axisLine={false} tickLine={false} tickFormatter={v=>`Rs ${(v/1000).toFixed(0)}k`} />
              <Tooltip content={<GlassTooltip />} />
              <Line type="monotone" dataKey="cumulativeProfit" stroke="#34d399" strokeWidth={2} dot={false}
                style={{filter:"drop-shadow(0 0 8px rgba(52,211,153,0.6))"}} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Action leaderboard */}
      {actionsSorted.length > 0 && (
        <div className="glass rounded-2xl p-6 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-amber-400" />Strategy Leaderboard (by Frequency)
          </h2>
          <div className="space-y-3">
            {actionsSorted.map(([action, count], idx) => {
              const total = history.length;
              const pct = Math.round((count / total) * 100);
              const col = actionColors[action] || "#94a3b8";
              return (
                <div key={action} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-lg flex items-center justify-center text-[10px] font-bold" style={{background:`${col}22`,color:col}}>#{idx+1}</span>
                      <span className="font-semibold text-white">{action}</span>
                    </div>
                    <span className="font-mono text-slate-400">{pct}% ({count} trials)</span>
                  </div>
                  <div className="h-1.5 rounded-full" style={{background:"rgba(255,255,255,0.06)"}}>
                    <div className="h-full rounded-full transition-all" style={{
                      width:`${pct}%`, background:col,
                      boxShadow:`0 0 8px ${col}80`,
                    }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {lastResult && (
        <div className="glass rounded-2xl p-4 text-xs" style={{border:"1px solid rgba(52,211,153,0.25)"}}>
          <div className="font-semibold text-emerald-400 mb-1">Last Batch Result:</div>
          <pre className="text-slate-400 font-mono overflow-x-auto">{JSON.stringify(lastResult, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
