import React, { useState, useEffect } from "react";
import { Sparkles, ArrowRight, ShieldCheck, Zap, Laptop, Clock, Layers, Star, Globe, Package, CheckCircle2 } from "lucide-react";
import { startNegotiation, fetchProducts } from "../api";

const PRESET_QUERIES = [
  "I need a gaming laptop under Rs 80,000, 32GB RAM, 1TB SSD, and delivery within 3 days.",
  "Looking for an Asus or Lenovo gaming laptop under 85k with 32GB RAM and fast dispatch",
  "Noise cancelling wireless headphones under Rs 25,000 for work within 2 days",
  "High performance Apple MacBook for 4K video editing under Rs 2,50,000"
];

export default function BuyerView({ onStartNegotiation }) {
  const [query, setQuery] = useState(PRESET_QUERIES[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [featuredProducts, setFeaturedProducts] = useState([]);

  useEffect(() => {
    fetchProducts({ limit: 6 }).then(data => {
      if (data && data.items) setFeaturedProducts(data.items);
    }).catch(console.error);
  }, []);

  async function handleSearch(e) {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    setLoading(true); setError(null);
    try {
      const res = await startNegotiation({ query: query.trim(), buyer_name: "Autonomous Shopping Agent", buyer_email: "buyer.agent@agentic.ai" });
      onStartNegotiation(res.negotiation_id);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10 space-y-12">

      {/* Razorpay Hero Section */}
      <div className="text-center space-y-5 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold" style={{
          background: "rgba(12,131,253,0.15)", border: "1px solid rgba(12,131,253,0.35)", color: "#38bdf8",
        }}>
          <Sparkles className="w-3.5 h-3.5 text-sky-400" />
          <span>POWERED BY RAZORPAY AGENTIC COMMERCE</span>
        </div>
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight text-white">
          Where Shopping Agents<br />
          Negotiate. <span style={{
            background: "linear-gradient(135deg, #0C83FD 0%, #00BAF2 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent"
          }}>Powered by Razorpay.</span>
        </h1>
        <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          AI Negotiates. Code Controls the Money. Razorpay Verifies. State your hardware specifications, budget cap, and delivery deadlines for autonomous micro-negotiations.
        </p>
      </div>

      {/* Razorpay Dispatch Prompt Terminal */}
      <div className="glass-strong rounded-3xl p-7 relative overflow-hidden" style={{
        border: "1px solid rgba(12,131,253,0.28)",
        boxShadow: "0 16px 48px rgba(2,4,43,0.8), 0 0 40px rgba(12,131,253,0.10)",
      }}>
        <div className="absolute -top-32 -right-32 w-72 h-72 rounded-full pointer-events-none" style={{
          background: "radial-gradient(circle, rgba(12,131,253,0.20) 0%, transparent 70%)",
        }} />
        <div className="absolute -bottom-20 -left-20 w-56 h-56 rounded-full pointer-events-none" style={{
          background: "radial-gradient(circle, rgba(0,186,242,0.15) 0%, transparent 70%)",
        }} />

        <form onSubmit={handleSearch} className="space-y-4 relative z-10">
          <div className="flex items-center justify-between">
            <label className="block text-xs font-bold uppercase tracking-widest text-sky-300">
              DISPATCH SHOPPING AGENT WITH CRITERIA:
            </label>
            <span className="text-[10px] font-mono text-slate-400">Razorpay Hybrid Semantic Search</span>
          </div>
          <div className="relative">
            <textarea rows={3} value={query} onChange={e => setQuery(e.target.value)}
              placeholder="e.g. I need a gaming laptop under Rs 80,000, 32GB RAM, 1TB SSD, delivery within 3 days."
              className="w-full rounded-2xl p-4 pr-44 text-sm text-white placeholder-slate-500 resize-none focus:outline-none transition-all"
              style={{
                background: "rgba(8,16,36,0.85)", border: "1px solid rgba(12,131,253,0.25)",
                backdropFilter: "blur(12px)",
              }}
              onFocus={e => { e.target.style.borderColor = "#0C83FD"; e.target.style.boxShadow = "0 0 0 3px rgba(12,131,253,0.20)"; }}
              onBlur={e => { e.target.style.borderColor = "rgba(12,131,253,0.25)"; e.target.style.boxShadow = "none"; }}
            />
            <button type="submit" disabled={loading}
              className="absolute right-3 bottom-3.5 flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-xs text-white disabled:opacity-50 transition-all cursor-pointer"
              style={{
                background: "#0C83FD",
                border: "1px solid rgba(255,255,255,0.20)",
                boxShadow: "0 0 24px rgba(12,131,253,0.40)",
              }}
              onMouseEnter={e => { e.currentTarget.style.background = "#0273E8"; e.currentTarget.style.boxShadow = "0 0 32px rgba(12,131,253,0.60)"; }}
              onMouseLeave={e => { e.currentTarget.style.background = "#0C83FD"; e.currentTarget.style.boxShadow = "0 0 24px rgba(12,131,253,0.40)"; }}
            >
              {loading ? (
                <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Dispatching...</span></>
              ) : (
                <><span>Dispatch Agent</span><ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-3 p-3 rounded-xl text-rose-300 text-xs" style={{
            background: "rgba(251,113,133,0.12)", border: "1px solid rgba(251,113,133,0.30)",
          }}>{error}</div>
        )}

        {/* Preset chips */}
        <div className="mt-5 pt-5 border-t border-sky-500/15 relative z-10">
          <div className="text-[11px] font-medium text-slate-400 mb-3 flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>One-click Agentic Commerce prompts:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {PRESET_QUERIES.map((preset, idx) => (
              <button key={idx} onClick={() => setQuery(preset)}
                className="text-xs px-3 py-1.5 rounded-lg text-slate-300 transition-all cursor-pointer"
                style={{
                  background: "rgba(12,131,253,0.08)", border: "1px solid rgba(12,131,253,0.20)",
                }}
                onMouseEnter={e => { e.currentTarget.style.background = "rgba(12,131,253,0.18)"; e.currentTarget.style.borderColor = "#0C83FD"; e.currentTarget.style.color = "#ffffff"; }}
                onMouseLeave={e => { e.currentTarget.style.background = "rgba(12,131,253,0.08)"; e.currentTarget.style.borderColor = "rgba(12,131,253,0.20)"; e.currentTarget.style.color = "#cbd5e1"; }}
              >
                "{preset.length > 52 ? preset.slice(0, 52) + "..." : preset}"
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Razorpay Feature Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {[
          { icon: ShieldCheck, color: "#0C83FD", title: "Razorpay Authoritative Ledger", desc: "Server-authoritative pricing. Client-side price tampering is cryptographically rejected via Razorpay HMAC-SHA256 signatures." },
          { icon: Layers, color: "#00BAF2", title: "Deterministic Pricing Core", desc: "Expected Profit = P(buy) × Margin. Zero LLM price hallucination, enforcing hard merchant profit margin floors." },
          { icon: Clock, color: "#00BA74", title: "LinUCB Contextual Bandit", desc: "Online exploration-exploitation reinforcement learning. Dynamically balances conversion likelihood with maximum retained margin." },
        ].map(({ icon: Icon, color, title, desc }) => (
          <div key={title} className="glass rounded-2xl p-6 space-y-3 hover:scale-[1.02] transition-transform" style={{
            border: `1px solid ${color}30`,
            boxShadow: `0 8px 24px rgba(2,4,43,0.6)`,
          }}>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{
              background: `${color}18`,
              border: `1px solid ${color}45`,
              boxShadow: `0 0 16px ${color}30`,
            }}>
              <Icon className="w-5 h-5" style={{ color }} />
            </div>
            <h3 className="text-sm font-bold text-white">{title}</h3>
            <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>

      {/* Catalog */}
      {featuredProducts.length > 0 && (
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Laptop className="w-5 h-5 text-sky-400" />
              <span>Razorpay Verified Real-World Catalog</span>
            </h2>
            <span className="text-xs text-slate-400">107+ SKUs with inventory &amp; margin metadata</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {featuredProducts.map(p => {
              const thumb = p.thumbnail_url || p.image_url;
              return (
                <div key={p.id} className="glass rounded-2xl p-4 flex flex-col justify-between space-y-3 hover:scale-[1.01] transition-all group"
                  style={{ border: "1px solid rgba(12,131,253,0.18)" }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = "#0C83FD"}
                  onMouseLeave={e => e.currentTarget.style.borderColor = "rgba(12,131,253,0.18)"}
                >
                  <div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 mb-2">
                      <span className="font-bold uppercase tracking-wider text-sky-400">{p.brand}</span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-amber-400 flex items-center gap-0.5">
                          <Star className="w-3 h-3 fill-amber-400" />{p.rating || 4.5}
                        </span>
                        <span className="px-1.5 py-0.5 rounded text-[9px]" style={{ background: "rgba(12,131,253,0.12)", color: "#7dd3fc" }}>{p.category}</span>
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      {thumb ? (
                        <img src={thumb} alt={p.title} className="w-14 h-14 rounded-xl object-cover shrink-0" style={{ border: "1px solid rgba(12,131,253,0.20)" }}
                          loading="lazy" onError={e => { e.target.style.display = "none"; }} />
                      ) : (
                        <div className="w-14 h-14 rounded-xl flex items-center justify-center shrink-0" style={{ background: "rgba(12,131,253,0.08)", border: "1px solid rgba(12,131,253,0.20)" }}>
                          <Package className="w-6 h-6 text-sky-400" />
                        </div>
                      )}
                      <div className="min-w-0 flex-1">
                        <h3 className="text-sm font-bold text-white line-clamp-2 leading-snug">{p.title}</h3>
                        {p.external_id && (
                          <span className="inline-flex items-center gap-1 mt-1 text-[9px] px-1.5 py-0.5 rounded" style={{ background: "rgba(12,131,253,0.15)", border: "1px solid rgba(12,131,253,0.30)", color: "#7dd3fc" }}>
                            <Globe className="w-2.5 h-2.5" />Verified Real SKU
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="mt-2.5 flex flex-wrap gap-1">
                      {p.specs?.ram_gb && <span className="text-[10px] px-1.5 py-0.5 rounded font-mono text-slate-300" style={{ background: "rgba(255,255,255,0.06)" }}>{p.specs.ram_gb}GB RAM</span>}
                      {p.specs?.storage_gb && <span className="text-[10px] px-1.5 py-0.5 rounded font-mono text-slate-300" style={{ background: "rgba(255,255,255,0.06)" }}>{p.specs.storage_gb >= 1000 ? `${p.specs.storage_gb / 1000}TB SSD` : `${p.specs.storage_gb}GB`}</span>}
                    </div>
                  </div>

                  <div className="pt-3 flex items-center justify-between" style={{ borderTop: "1px solid rgba(12,131,253,0.15)" }}>
                    <div>
                      <div className="text-base font-extrabold text-white">Rs {p.base_price.toLocaleString("en-IN")}</div>
                      <div className="text-[10px] text-emerald-400">Margin: Rs {p.margin?.toLocaleString("en-IN")} ({p.margin_pct}%)</div>
                    </div>
                    <button onClick={() => setQuery(`I want to negotiate for the ${p.title} under Rs ${Math.round(p.base_price * 0.94)}`)}
                      className="px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
                      style={{ background: "#0C83FD", color: "white", boxShadow: "0 0 14px rgba(12,131,253,0.30)" }}
                      onMouseEnter={e => { e.currentTarget.style.background = "#0273E8"; }}
                      onMouseLeave={e => { e.currentTarget.style.background = "#0C83FD"; }}
                    >Negotiate</button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
