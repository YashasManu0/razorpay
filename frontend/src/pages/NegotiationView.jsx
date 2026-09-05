import React, { useState, useEffect, useRef } from "react";
import { Send, User, CheckCircle2, Sparkles, HelpCircle, ArrowRight, Award, Package, AlertCircle, Star } from "lucide-react";
import { fetchNegotiationDetails, sendNegotiationMessage } from "../api";

export default function NegotiationView({ negotiationId, onProceedToPayment, onInspectOffer }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [counterPrice, setCounterPrice] = useState("");
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => { if (negotiationId) loadData(); }, [negotiationId]);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [data?.messages]);

  async function loadData() {
    try { setLoading(true); const res = await fetchNegotiationDetails(negotiationId); setData(res); }
    catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  async function handleSendMessage(msgText, customPrice = null) {
    if (!msgText.trim()) return;
    setSending(true); setError(null);
    try {
      const payload = { message: msgText.trim(), counter_price: customPrice ? parseFloat(customPrice) : undefined };
      const res = await sendNegotiationMessage(negotiationId, payload);
      if (res.order_id && (res.status === "ACCEPTED" || res.status === "PAYMENT_PENDING")) {
        await loadData();
        onProceedToPayment(res.order_id);
      } else {
        await loadData();
        setInputMessage("");
        setCounterPrice("");
      }
    } catch (err) {
      setError(err.message);
      await loadData();
    } finally { setSending(false); }
  }

  function handleAcceptOffer() { handleSendMessage("I accept this offer. Let'\''s proceed to payment!"); }

  if (loading && !data) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 rounded-full animate-spin" style={{borderColor:"rgba(12,131,253,0.3)",borderTopColor:"#0C83FD"}} />
        <p className="text-xs text-slate-400">Loading Razorpay negotiation session...</p>
      </div>
    </div>
  );

  const activeOffer = data?.active_offer;
  const product = data?.product;
  const isAcceptedOrPending = ["ACCEPTED","PAYMENT_PENDING"].includes(data?.status);
  const isTerminated = ["PAID","COMPLETED","EXPIRED","REJECTED","ACCEPTED","PAYMENT_PENDING"].includes(data?.status);

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">

      {/* Session Breadcrumb */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5 mb-6" style={{borderBottom:"1px solid rgba(12,131,253,0.18)"}}>
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-slate-400 font-medium">Session ID:</span>
            <span className="text-xs font-mono text-sky-300 font-semibold">{negotiationId?.slice(0,16)}...</span>
            <span className="text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full"
              style={{
                background: isAcceptedOrPending ? "rgba(0,186,116,0.15)" : "rgba(12,131,253,0.15)",
                border: isAcceptedOrPending ? "1px solid rgba(0,186,116,0.35)" : "1px solid rgba(12,131,253,0.35)",
                color: isAcceptedOrPending ? "#6ee7b7" : "#38bdf8"
              }}>
              {data?.status}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Buyer: <span className="text-white font-medium">{data?.buyer?.name}</span> — Round <span className="text-white font-bold">{data?.current_round}</span> of {data?.max_rounds}
          </p>
        </div>
        {activeOffer && (
          <button onClick={() => onInspectOffer(activeOffer.id)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer"
            style={{background:"rgba(104,81,255,0.15)",border:"1px solid rgba(104,81,255,0.35)",color:"#c4b5fd"}}
            onMouseEnter={e => e.currentTarget.style.background="rgba(104,81,255,0.25)"}
            onMouseLeave={e => e.currentTarget.style.background="rgba(104,81,255,0.15)"}
          >
            <HelpCircle className="w-4 h-4" />
            <span>Why ₹{activeOffer.offer_price.toLocaleString("en-IN")}?</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Chat Panel */}
        <div className="lg:col-span-8 flex flex-col h-[72vh] rounded-2xl overflow-hidden glass-strong" style={{
          border:"1px solid rgba(12,131,253,0.20)", boxShadow:"0 16px 48px rgba(2,4,43,0.8)",
        }}>
          <div className="flex-1 p-5 overflow-y-auto space-y-4">
            {data?.messages?.map(m => {
              const isBuyer = m.sender_role === "buyer";
              return (
                <div key={m.id} className={`flex items-start gap-3 ${isBuyer ? "justify-end" : "justify-start"}`}>
                  {!isBuyer && (
                    <div className="w-8 h-8 rounded-xl flex items-center justify-center text-white shrink-0 mt-0.5" style={{
                      background:"linear-gradient(135deg,#0C2340 0%,#0C83FD 100%)",
                      border:"1px solid rgba(12,131,253,0.40)",
                      boxShadow:"0 0 12px rgba(12,131,253,0.30)",
                    }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                        <path d="M14.5 2L5 14H11L9.5 22L19 10H13L14.5 2Z" fill="#0C83FD" stroke="#00BAF2" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                  )}
                  <div className={`max-w-xl p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${isBuyer ? "rounded-tr-none" : "rounded-tl-none"}`}
                    style={isBuyer
                      ? {background:"#0C83FD",color:"white",boxShadow:"0 0 20px rgba(12,131,253,0.35)"}
                      : {background:"rgba(8,16,36,0.90)",border:"1px solid rgba(12,131,253,0.20)"}
                    }
                  >
                    <div className="flex items-center justify-between text-[10px] opacity-75 mb-1">
                      <span className="font-bold uppercase tracking-wider">{isBuyer ? "Buyer Agent" : "Razorpay Merchant AI"}</span>
                      <span>{new Date(m.timestamp).toLocaleTimeString([], { hour:"2-digit", minute:"2-digit" })}</span>
                    </div>
                    <p className="whitespace-pre-line text-white">{m.message_text}</p>
                  </div>
                  {isBuyer && (
                    <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5" style={{background:"rgba(255,255,255,0.10)",border:"1px solid rgba(255,255,255,0.20)"}}>
                      <User className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          {error && (
            <div className="px-4 py-2.5 text-rose-300 text-xs flex items-center gap-2" style={{background:"rgba(251,113,133,0.12)",borderTop:"1px solid rgba(251,113,133,0.25)"}}>
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" /><span>{error}</span>
            </div>
          )}

          {!isTerminated && activeOffer && (
            <div className="p-3 flex items-center gap-2 overflow-x-auto text-xs" style={{background:"rgba(8,16,36,0.60)",borderTop:"1px solid rgba(12,131,253,0.15)"}}>
              <span className="text-[11px] text-slate-400 shrink-0 font-medium">Quick Counter:</span>
              {[{ pct:0.96, label:"-4%" }, { pct:0.93, label:"-7%" }].map(({ pct, label }) => {
                const target = Math.round(activeOffer.offer_price * pct);
                return (
                  <button key={label} disabled={sending} onClick={() => handleSendMessage(`Can you do ₹${target.toLocaleString("en-IN")}?`, target)}
                    className="px-3 py-1 rounded-lg text-slate-200 shrink-0 transition-all cursor-pointer font-medium"
                    style={{background:"rgba(12,131,253,0.10)",border:"1px solid rgba(12,131,253,0.25)"}}
                    onMouseEnter={e => { e.currentTarget.style.background="rgba(12,131,253,0.22)"; e.currentTarget.style.borderColor="#0C83FD"; }}
                    onMouseLeave={e => { e.currentTarget.style.background="rgba(12,131,253,0.10)"; e.currentTarget.style.borderColor="rgba(12,131,253,0.25)"; }}
                  >
                    Request {label} (₹{target.toLocaleString("en-IN")})
                  </button>
                );
              })}
            </div>
          )}

          {/* Bottom input or Payment Notice */}
          {isAcceptedOrPending ? (
            <div className="p-3.5 flex items-center justify-between gap-3" style={{background:"rgba(2,4,43,0.92)",borderTop:"1px solid rgba(12,131,253,0.25)"}}>
              <div className="text-xs text-emerald-400 font-medium flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Offer terms accepted! Price is cryptographically locked.</span>
              </div>
              {data?.order && (
                <button onClick={() => onProceedToPayment(data.order.id)}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-white flex items-center gap-1.5 shrink-0 transition-all cursor-pointer"
                  style={{background:"linear-gradient(135deg,#00BA74,#0C83FD)",boxShadow:"0 0 18px rgba(0,186,116,0.40)"}}
                >
                  <span>Go to Checkout ({data.order.order_number})</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          ) : (
            <div className="p-3 flex items-center gap-2" style={{background:"rgba(2,4,43,0.85)",borderTop:"1px solid rgba(12,131,253,0.18)"}}>
              <input type="text" value={inputMessage} disabled={isTerminated || sending}
                onChange={e => setInputMessage(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") handleSendMessage(inputMessage, counterPrice); }}
                placeholder={isTerminated ? "Negotiation concluded." : "Type counter-offer (e.g. Can you do ₹76,000?)..."}
                className="flex-1 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white focus:outline-none transition-all"
                style={{background:"rgba(8,16,36,0.90)",border:"1px solid rgba(12,131,253,0.25)"}}
              />
              <button onClick={() => handleSendMessage(inputMessage, counterPrice)} disabled={isTerminated || sending || !inputMessage.trim()}
                className="p-2.5 rounded-xl text-white transition-all disabled:opacity-40 cursor-pointer"
                style={{background:"#0C83FD",boxShadow:"0 0 16px rgba(12,131,253,0.40)"}}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Offer Panel */}
        <div className="lg:col-span-4 space-y-4">
          {activeOffer ? (
            <div className="rounded-2xl p-5 space-y-4 relative overflow-hidden glass-strong" style={{
              border:"1px solid rgba(12,131,253,0.30)", boxShadow:"0 0 40px rgba(12,131,253,0.10), 0 16px 48px rgba(2,4,43,0.7)",
            }}>
              <div className="absolute top-0 right-0 px-3 py-1 text-[10px] font-bold text-white uppercase tracking-wider rounded-bl-xl" style={{
                background:"linear-gradient(135deg,#0C2340 0%,#0C83FD 100%)",
                borderBottom:"1px solid rgba(12,131,253,0.40)",
                borderLeft:"1px solid rgba(12,131,253,0.40)",
              }}>Razorpay Active Offer</div>

              <div className="flex items-start gap-3 pt-3">
                {(product?.thumbnail_url || product?.image_url) && (
                  <img src={product.thumbnail_url || product.image_url} alt={product.title}
                    className="w-16 h-16 rounded-xl object-cover shrink-0" style={{border:"1px solid rgba(12,131,253,0.25)"}}
                    loading="lazy" onError={e => { e.target.style.display="none"; }} />
                )}
                <div className="min-w-0 flex-1">
                  <span className="text-[10px] font-mono text-sky-400 uppercase font-bold">{product?.brand}</span>
                  {product?.rating && <span className="ml-2 text-[10px] text-amber-400 inline-flex items-center gap-0.5"><Star className="w-3 h-3 fill-amber-400" />{product.rating}</span>}
                  <h3 className="text-sm font-bold text-white line-clamp-2 leading-snug mt-0.5">{product?.title}</h3>
                  <div className="text-[10px] text-slate-400 mt-1">Available Stock: {product?.available_stock} units</div>
                </div>
              </div>

              <div className="p-4 rounded-xl space-y-1" style={{background:"rgba(8,16,36,0.85)",border:"1px solid rgba(12,131,253,0.20)"}}>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-extrabold text-white">
                    ₹{activeOffer.offer_price.toLocaleString("en-IN")}
                  </span>
                  {activeOffer.discount_pct > 0 && (
                    <span className="text-xs text-slate-400 line-through">₹{activeOffer.list_price?.toLocaleString("en-IN")}</span>
                  )}
                </div>
                {activeOffer.discount_pct > 0 && (
                  <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{activeOffer.discount_pct.toFixed(1)}% Saved (₹{activeOffer.discount_amount?.toLocaleString("en-IN")})</span>
                  </div>
                )}
              </div>

              <div className="space-y-2 text-xs">
                <div className="font-semibold text-sky-300 text-[10px] uppercase tracking-wider">Authorized Inclusions:</div>
                <ul className="space-y-1.5">
                  <li className="flex items-center gap-2 text-slate-200">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>{activeOffer.free_shipping ? "Complimentary Express Delivery (Save ₹500)" : "Standard 3-Day Delivery"}</span>
                  </li>
                  <li className="flex items-center gap-2 text-slate-200">
                    <Award className="w-4 h-4 text-sky-400 shrink-0" />
                    <span>{activeOffer.warranty_months}-Month Official Brand Warranty</span>
                  </li>
                  {activeOffer.bundle_items?.map((b, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-violet-300 font-medium">
                      <Package className="w-4 h-4 text-violet-400 shrink-0" />
                      <span>{b.name} (Worth ₹{b.retail_val?.toLocaleString("en-IN")})</span>
                    </li>
                  ))}
                </ul>
              </div>

              {isAcceptedOrPending ? (
                <button onClick={() => data?.order && onProceedToPayment(data.order.id)}
                  className="w-full py-3.5 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all cursor-pointer text-white"
                  style={{
                    background: "linear-gradient(135deg,#00BA74,#0C83FD)",
                    border: "1px solid rgba(0,186,116,0.50)",
                    boxShadow: "0 0 24px rgba(0,186,116,0.35)",
                  }}
                >
                  <span>Proceed to Razorpay Checkout</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              ) : (
                <button onClick={handleAcceptOffer} disabled={sending}
                  className="w-full py-3.5 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer text-white"
                  style={{
                    background: "#00BA74",
                    border: "1px solid rgba(0,186,116,0.50)",
                    boxShadow: "0 0 24px rgba(0,186,116,0.35)",
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = "#00A35C"; }}
                  onMouseLeave={e => { e.currentTarget.style.background = "#00BA74"; }}
                >
                  <span>Accept Offer & Proceed to Checkout</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          ) : (
            <div className="p-6 rounded-2xl text-center text-slate-400 text-xs glass">
              Matching specs against merchant inventory...
            </div>
          )}

          {activeOffer && (
            <div className="p-4 rounded-xl space-y-2 text-xs glass" style={{border:"1px solid rgba(12,131,253,0.18)"}}>
              <div className="font-semibold text-sky-300 uppercase tracking-wider text-[10px]">Merchant Decision Telemetry</div>
              <div className="grid grid-cols-2 gap-2">
                <div className="p-2.5 rounded-lg" style={{background:"rgba(8,16,36,0.80)",border:"1px solid rgba(12,131,253,0.15)"}}>
                  <div className="text-[10px] text-slate-400">P(Conversion)</div>
                  <div className="text-sm font-mono font-bold text-sky-400">{(activeOffer.p_conversion * 100).toFixed(1)}%</div>
                </div>
                <div className="p-2.5 rounded-lg" style={{background:"rgba(8,16,36,0.80)",border:"1px solid rgba(12,131,253,0.15)"}}>
                  <div className="text-[10px] text-slate-400">Expected Profit</div>
                  <div className="text-sm font-mono font-bold text-emerald-400">₹{activeOffer.expected_profit?.toLocaleString("en-IN")}</div>
                </div>
              </div>
              <div className="text-[11px] text-slate-400 italic">
                Active Rule: <span className="text-emerald-400 not-italic font-mono">{activeOffer.reason_code}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
