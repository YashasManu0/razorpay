import React, { useState, useEffect } from "react";
import { Package, Search, Globe, Star, RefreshCw } from "lucide-react";
import { fetchProducts, syncRealWorldProducts } from "../api";

const CATEGORIES = ["all","laptops","smartphones","monitors","tablets","audio","watches","accessories"];
const CAT_COLORS = { laptops:"rgba(56,189,248,", smartphones:"rgba(52,211,153,", monitors:"rgba(99,102,241,", tablets:"rgba(167,139,250,", audio:"rgba(251,191,36,", watches:"rgba(251,113,133,", accessories:"rgba(34,211,238," };

export default function ProductsView() {
  const [products, setProducts] = useState([]);
  const [selectedCat, setSelectedCat] = useState("all");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncNotice, setSyncNotice] = useState(null);

  useEffect(() => { loadProducts(); }, [selectedCat, search]);

  async function loadProducts() {
    try {
      setLoading(true);
      const params = { limit: 150 };
      if (selectedCat !== "all") params.category = selectedCat;
      if (search.trim()) params.search = search.trim();
      const res = await fetchProducts(params);
      setProducts(res.items || []);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  }

  async function handleSyncRealWorld() {
    try {
      setSyncing(true); setSyncNotice(null);
      const res = await syncRealWorldProducts();
      setSyncNotice(`Synced! ${res.imported || 0} imported, ${res.updated || 0} updated.`);
      await loadProducts();
      setTimeout(() => setSyncNotice(null), 5000);
    } catch (err) { setSyncNotice(`Sync failed: ${err.message}`); } finally { setSyncing(false); }
  }

  const col = (c) => (CAT_COLORS[c] || "rgba(56,189,248,");

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5" style={{borderBottom:"1px solid rgba(255,255,255,0.08)"}}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center" style={{background:"rgba(56,189,248,0.15)",border:"1px solid rgba(56,189,248,0.35)",boxShadow:"0 0 16px rgba(56,189,248,0.20)"}}>
            <Package className="w-6 h-6 text-sky-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Product Catalog Management</h1>
            <p className="text-xs text-slate-500">{products.length} products in view — Real-world SKUs via live API</p>
          </div>
        </div>
        <button onClick={handleSyncRealWorld} disabled={syncing}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white disabled:opacity-40 transition-all"
          style={{background:"rgba(52,211,153,0.15)",border:"1px solid rgba(52,211,153,0.35)"}}
          onMouseEnter={e => e.currentTarget.style.boxShadow="0 0 16px rgba(52,211,153,0.25)"}
          onMouseLeave={e => e.currentTarget.style.boxShadow="none"}
        >
          {syncing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4" />}
          <span>Sync Live Products</span>
        </button>
      </div>

      {syncNotice && (
        <div className="p-3 rounded-xl text-xs" style={{background:"rgba(52,211,153,0.10)",border:"1px solid rgba(52,211,153,0.25)",color:"#6ee7b7"}}>
          {syncNotice}
        </div>
      )}

      {/* Search + Category Filter */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search products..." className="input-glass w-full rounded-xl pl-9 pr-4 py-2 text-xs"
          />
        </div>
        <div className="flex flex-wrap gap-1.5">
          {CATEGORIES.map(c => (
            <button key={c} onClick={() => setSelectedCat(c)}
              className="px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all"
              style={selectedCat === c
                ? {background:`${col(c)}0.18)`,border:`1px solid ${col(c)}0.45)`,color:"white",boxShadow:`0 0 12px ${col(c)}0.20)`}
                : {background:"rgba(255,255,255,0.05)",border:"1px solid rgba(255,255,255,0.10)",color:"#94a3b8"}
              }
            >{c}</button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{borderColor:"rgba(56,189,248,0.3)",borderTopColor:"#38bdf8"}} />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {products.map(p => {
            const c = col(p.category);
            const thumb = p.thumbnail_url || p.image_url;
            return (
              <div key={p.id} className="glass rounded-2xl p-4 space-y-3 hover:scale-[1.02] transition-all"
                onMouseEnter={e => { e.currentTarget.style.borderColor=`${c}0.40)`; e.currentTarget.style.boxShadow=`0 0 20px ${c}0.12)`; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor="rgba(255,255,255,0.10)"; e.currentTarget.style.boxShadow=""; }}
              >
                <div className="flex items-start gap-3">
                  {thumb ? (
                    <img src={thumb} alt={p.title} className="w-12 h-12 rounded-xl object-cover shrink-0" style={{border:"1px solid rgba(255,255,255,0.10)"}}
                      loading="lazy" onError={e => { e.target.style.display="none"; }} />
                  ) : (
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0" style={{background:"rgba(255,255,255,0.06)",border:"1px solid rgba(255,255,255,0.10)"}}>
                      <Package className="w-5 h-5 text-slate-500" />
                    </div>
                  )}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-1 mb-0.5">
                      <span className="text-[10px] uppercase font-bold tracking-wide" style={{color:`${c}1)`}}>{p.brand}</span>
                      {p.rating && <span className="text-[10px] text-amber-400 flex items-center gap-0.5"><Star className="w-3 h-3 fill-amber-400" />{p.rating}</span>}
                    </div>
                    <h3 className="text-xs font-bold text-white line-clamp-2 leading-snug">{p.title}</h3>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1">
                  <span className="text-[9px] px-1.5 py-0.5 rounded capitalize" style={{background:`${c}0.12)`,border:`1px solid ${c}0.25)`,color:`${c}1)`}}>{p.category}</span>
                  {p.external_id && <span className="text-[9px] px-1.5 py-0.5 rounded flex items-center gap-0.5" style={{background:"rgba(56,189,248,0.10)",border:"1px solid rgba(56,189,248,0.25)",color:"#7dd3fc"}}><Globe className="w-2.5 h-2.5" />Live</span>}
                  {p.specs?.ram_gb && <span className="text-[9px] px-1.5 py-0.5 rounded font-mono" style={{background:"rgba(255,255,255,0.06)",color:"#94a3b8"}}>{p.specs.ram_gb}GB</span>}
                </div>

                <div className="flex items-center justify-between pt-2" style={{borderTop:"1px solid rgba(255,255,255,0.07)"}}>
                  <div>
                    <div className="text-sm font-extrabold text-white">Rs {p.base_price?.toLocaleString("en-IN")}</div>
                    <div className="text-[10px] text-emerald-400">{p.margin_pct}% margin</div>
                  </div>
                  <div className="text-[10px] text-slate-500">Stock: {p.available_stock}</div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
