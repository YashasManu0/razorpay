import React, { useState } from "react";
import {
  Store, ShoppingBag, ShieldAlert, BarChart3,
  Settings, Package, Database, Cpu, HelpCircle, Activity,
  Menu, X
} from "lucide-react";

const NAV_ITEMS = [
  { id: "buyer",      label: "Buyer Agent",      icon: ShoppingBag },
  { id: "merchant",   label: "Merchant Cockpit", icon: Store       },
  { id: "products",   label: "Products",          icon: Package     },
  { id: "policies",   label: "Policies",          icon: Settings    },
  { id: "inventory",  label: "Inventory",         icon: Database    },
  { id: "analytics",  label: "Analytics & Lift",  icon: BarChart3   },
  { id: "audit",      label: "Why This Price?",   icon: HelpCircle  },
  { id: "simulation", label: "Bandit Sim",        icon: Cpu         },
];

export default function Navbar({ currentView, setView, onOpenFailureModal, activeNegotiationId }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  function nav(v) { setView(v); setMobileOpen(false); }

  return (
    <header className="sticky top-0 z-40" style={{
      background: "rgba(2,4,43,0.88)",
      backdropFilter: "blur(24px)",
      WebkitBackdropFilter: "blur(24px)",
      borderBottom: "1px solid rgba(12,131,253,0.20)",
    }}>
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6">
        <div className="flex items-center h-14 gap-3">

          {/* Razorpay Brand Mark & Logo */}
          <button onClick={() => nav("buyer")} className="flex items-center gap-2.5 shrink-0 group select-none">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform" style={{
              background: "linear-gradient(135deg, #0C2340 0%, #0C83FD 100%)",
              border: "1px solid rgba(12,131,253,0.40)",
              boxShadow: "0 0 16px rgba(12,131,253,0.35)",
            }}>
              {/* Razorpay iconic lightning / slash SVG */}
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M14.5 2L5 14H11L9.5 22L19 10H13L14.5 2Z" fill="#0C83FD" stroke="#00BAF2" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div className="hidden sm:block text-left">
              <div className="flex items-center gap-2">
                <span className="text-sm font-extrabold tracking-tight text-white whitespace-nowrap">
                  Razorpay <span className="font-semibold text-sky-400">Agent Negotiator</span>
                </span>
                <span className="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded whitespace-nowrap" style={{
                  background: "rgba(12,131,253,0.18)",
                  border: "1px solid rgba(12,131,253,0.40)",
                  color: "#38bdf8",
                }}>Agentic Commerce</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-tight mt-0.5 hidden 2xl:block whitespace-nowrap">
                AI Negotiates • Code Controls Money • Razorpay Verifies
              </p>
            </div>
          </button>

          {/* Desktop Nav Tabs */}
          <nav className="hidden xl:flex items-center gap-1 flex-1 justify-center">
            {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
              const isActive = currentView === id;
              return (
                <button key={id} onClick={() => nav(id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-medium whitespace-nowrap transition-all border ${
                    isActive
                      ? "bg-[#0C83FD] text-white border-[#0C83FD] shadow-[0_0_16px_rgba(12,131,253,0.40)] font-semibold"
                      : "border-transparent text-slate-300 hover:text-white hover:bg-[#0C83FD]/10 hover:border-[#0C83FD]/20"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5 shrink-0" />
                  <span>{label}</span>
                </button>
              );
            })}
            {activeNegotiationId && (
              <button onClick={() => nav("negotiation")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-medium whitespace-nowrap transition-all border ${
                  currentView === "negotiation"
                    ? "bg-[#00BA74] text-white border-[#00BA74] shadow-[0_0_16px_rgba(0,186,116,0.35)] font-semibold"
                    : "border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
                }`}
              >
                <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse shrink-0" />
                <span>Live Negotiation</span>
              </button>
            )}
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-2 ml-auto shrink-0">
            <button onClick={onOpenFailureModal}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold whitespace-nowrap transition-all shrink-0 cursor-pointer"
              style={{
                background: "rgba(251,113,133,0.12)",
                border: "1px solid rgba(251,113,133,0.35)",
                color: "#fda4af",
                boxShadow: "0 0 12px rgba(251,113,133,0.15)",
              }}
              onMouseEnter={e => { e.currentTarget.style.boxShadow = "0 0 20px rgba(251,113,133,0.40)"; e.currentTarget.style.background = "rgba(251,113,133,0.20)"; }}
              onMouseLeave={e => { e.currentTarget.style.boxShadow = "0 0 12px rgba(251,113,133,0.15)"; e.currentTarget.style.background = "rgba(251,113,133,0.12)"; }}
            >
              <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
              <span>BREAK THE AGENT</span>
              <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping shrink-0" />
            </button>
            <button onClick={() => setMobileOpen(o => !o)}
              className="xl:hidden p-1.5 rounded-lg text-slate-400 hover:text-white transition-colors"
              style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.10)" }}
            >
              {mobileOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="xl:hidden px-4 py-3 space-y-1" style={{
          background: "rgba(2,4,43,0.95)", borderTop: "1px solid rgba(12,131,253,0.18)",
        }}>
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
            const isActive = currentView === id;
            return (
              <button key={id} onClick={() => nav(id)}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all border ${
                  isActive ? "bg-[#0C83FD] text-white border-[#0C83FD]" : "border-transparent text-slate-300 hover:bg-[#0C83FD]/10"
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" /><span>{label}</span>
              </button>
            );
          })}
          {activeNegotiationId && (
            <button onClick={() => nav("negotiation")}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium border border-emerald-400/30 bg-emerald-400/10 text-emerald-300"
            >
              <Activity className="w-4 h-4 text-emerald-400 animate-pulse" /><span>Live Negotiation</span>
            </button>
          )}
        </div>
      )}
    </header>
  );
}
