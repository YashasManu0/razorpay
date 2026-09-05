import React, { useState, useEffect } from "react";
import { Database, AlertTriangle, Clock, Plus, Search, CheckCircle2 } from "lucide-react";
import { fetchInventory, updateInventory } from "../api";

const FILTERS = ["all", "low_stock", "aging"];

export default function InventoryView() {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [actionNotice, setActionNotice] = useState(null);

  useEffect(() => { loadInventory(); }, [filter]);

  async function loadInventory() {
    try {
      setLoading(true);
      const res = await fetchInventory({ filter_status: filter !== "all" ? filter : undefined });
      setItems(res || []);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  }

  async function handleRestock(invId, currentQty) {
    try {
      await updateInventory(invId, { quantity: (currentQty || 0) + 10 });
      setActionNotice("Stock updated (+10 units)");
      setTimeout(() => setActionNotice(null), 3000);
      await loadInventory();
    } catch (e) { console.error(e); }
  }

  async function handleAgeItem(invId, currentAge) {
    try {
      await updateInventory(invId, { age_days: (currentAge || 0) + 30 });
      setActionNotice("Item age increased (+30 days)");
      setTimeout(() => setActionNotice(null), 3000);
      await loadInventory();
    } catch (e) { console.error(e); }
  }

  const filteredItems = items.filter(item => {
    if (!search.trim()) return true;
    const title = (item.product_title || item.product?.title || "").toLowerCase();
    const brand = (item.brand || item.product?.brand || "").toLowerCase();
    const cat = (item.category || item.product?.category || "").toLowerCase();
    const q = search.toLowerCase();
    return title.includes(q) || brand.includes(q) || cat.includes(q);
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5" style={{borderBottom:"1px solid rgba(12,131,253,0.18)"}}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center" style={{
            background: "rgba(12,131,253,0.15)",
            border: "1px solid rgba(12,131,253,0.35)",
            boxShadow: "0 0 16px rgba(12,131,253,0.25)",
          }}>
            <Database className="w-5 h-5 text-sky-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Razorpay Inventory &amp; Warehouse Ledger</h1>
            <p className="text-xs text-slate-400">Real-time stock reservation, shelf-life aging &amp; scarcity guard trigger simulation</p>
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex gap-2">
          {FILTERS.map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all cursor-pointer"
              style={filter === f
                ? {background:"#0C83FD",color:"white",boxShadow:"0 0 14px rgba(12,131,253,0.40)"}
                : {background:"rgba(8,16,36,0.80)",border:"1px solid rgba(12,131,253,0.20)",color:"#94a3b8"}
              }
            >
              {f.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Search Bar & Action Notice */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="relative flex-1 min-w-56 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by product title, brand, or category..."
            className="w-full pl-9 pr-4 py-2 rounded-xl text-xs text-white focus:outline-none transition-all"
            style={{background:"rgba(8,16,36,0.85)",border:"1px solid rgba(12,131,253,0.25)"}}
          />
        </div>
        {actionNotice && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium text-emerald-300" style={{background:"rgba(0,186,116,0.15)",border:"1px solid rgba(0,186,116,0.35)"}}>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>{actionNotice}</span>
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{borderColor:"rgba(12,131,253,0.3)",borderTopColor:"#0C83FD"}} />
        </div>
      ) : (
        <div className="glass-strong rounded-2xl overflow-hidden" style={{border:"1px solid rgba(12,131,253,0.20)",boxShadow:"0 16px 48px rgba(2,4,43,0.8)"}}>
          <table className="w-full text-left table-glass">
            <thead>
              <tr style={{background:"rgba(8,16,36,0.95)",borderBottom:"1px solid rgba(12,131,253,0.20)"}}>
                <th className="py-3 px-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Product</th>
                <th className="py-3 px-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Category</th>
                <th className="py-3 px-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Brand</th>
                <th className="py-3 px-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Stock</th>
                <th className="py-3 px-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Base Price</th>
                <th className="py-3 px-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Policy Status</th>
                <th className="py-3 px-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider">Age</th>
                <th className="py-3 px-4 text-[11px] font-bold text-slate-400 uppercase tracking-wider text-right">Simulation Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map(item => {
                const invId = item.inventory_id || item.id;
                const title = item.product_title || item.product?.title || "Unknown Product";
                const category = item.category || item.product?.category || "--";
                const brand = item.brand || item.product?.brand || "--";
                const stock = item.available_stock ?? item.quantity ?? 0;
                const isLowStock = stock <= 5;
                const isAging = item.age_days >= 60;
                const price = item.base_price || item.product?.base_price || 0;

                return (
                  <tr key={invId} className="border-b border-sky-500/10 hover:bg-[#0C83FD]/5 transition-colors">
                    <td className="py-3 px-4 font-semibold text-white max-w-[220px] truncate" title={title}>
                      {title}
                    </td>
                    <td className="py-3 px-4 capitalize text-slate-300 text-xs">
                      {category}
                    </td>
                    <td className="py-3 px-4 text-sky-400 font-mono text-[11px] font-bold">
                      {brand}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-extrabold font-mono text-sm" style={{color: isLowStock ? "#fb7185" : "#00BA74"}}>
                        {stock} units
                      </span>
                    </td>
                    <td className="py-3 px-4 font-bold text-white text-xs">
                      ₹{price.toLocaleString("en-IN")}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {isLowStock && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1" style={{background:"rgba(251,113,133,0.15)",border:"1px solid rgba(251,113,133,0.40)",color:"#fda4af"}}>
                            <AlertTriangle className="w-3 h-3" />Low Stock Guard
                          </span>
                        )}
                        {isAging && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1" style={{background:"rgba(255,153,0,0.15)",border:"1px solid rgba(255,153,0,0.40)",color:"#fbbf24"}}>
                            <Clock className="w-3 h-3" />Aging Clearance (+3%)
                          </span>
                        )}
                        {!isLowStock && !isAging && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full font-bold" style={{background:"rgba(0,186,116,0.15)",border:"1px solid rgba(0,186,116,0.40)",color:"#6ee7b7"}}>
                            Optimal Policy
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono text-xs" style={{color: isAging ? "#fbbf24" : "#94a3b8"}}>
                      {item.age_days}d
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleRestock(invId, item.quantity || stock)}
                          className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer"
                          style={{background:"rgba(0,186,116,0.15)",border:"1px solid rgba(0,186,116,0.40)",color:"#6ee7b7"}}
                          onMouseEnter={e => e.currentTarget.style.background = "rgba(0,186,116,0.25)"}
                          onMouseLeave={e => e.currentTarget.style.background = "rgba(0,186,116,0.15)"}
                          title="Restock 10 units"
                        >
                          <Plus className="w-3 h-3" />+10 Stock
                        </button>
                        <button
                          onClick={() => handleAgeItem(invId, item.age_days)}
                          className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer"
                          style={{background:"rgba(12,131,253,0.15)",border:"1px solid rgba(12,131,253,0.40)",color:"#38bdf8"}}
                          onMouseEnter={e => e.currentTarget.style.background = "rgba(12,131,253,0.25)"}
                          onMouseLeave={e => e.currentTarget.style.background = "rgba(12,131,253,0.15)"}
                          title="Simulate 30 days of warehouse aging"
                        >
                          <Clock className="w-3 h-3" />+30d Age
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
