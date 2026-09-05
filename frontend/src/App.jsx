import React, { useState } from 'react';
import Navbar from './components/Navbar';
import FailureInjectionModal from './components/FailureInjectionModal';

// Pages
import BuyerView from './pages/BuyerView';
import NegotiationView from './pages/NegotiationView';
import PaymentView from './pages/PaymentView';
import OrderView from './pages/OrderView';
import MerchantDashboardView from './pages/MerchantDashboardView';
import ProductsView from './pages/ProductsView';
import PoliciesView from './pages/PoliciesView';
import InventoryView from './pages/InventoryView';
import AnalyticsView from './pages/AnalyticsView';
import AuditView from './pages/AuditView';
import SimulationView from './pages/SimulationView';

export default function App() {
  const [currentView, setView] = useState(() => new URLSearchParams(window.location.search).get('view') || 'buyer');
  const [activeNegotiationId, setActiveNegotiationId] = useState(null);
  const [activeOrderId, setActiveOrderId] = useState(null);
  const [selectedOfferIdForAudit, setSelectedOfferIdForAudit] = useState(null);
  const [isFailureModalOpen, setIsFailureModalOpen] = useState(false);

  function handleStartNegotiation(negId) {
    setActiveNegotiationId(negId);
    setView('negotiation');
  }

  function handleProceedToPayment(orderId) {
    setActiveOrderId(orderId);
    setView('payment');
  }

  function handlePaymentComplete(orderId) {
    setActiveOrderId(orderId);
    setView('order');
  }

  function handleInspectOffer(offerId) {
    setSelectedOfferIdForAudit(offerId);
    setView('audit');
  }

  function handleStartNew() {
    setActiveNegotiationId(null);
    setActiveOrderId(null);
    setView('buyer');
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#0a0d14] text-slate-100">
      
      {/* Top Navbar */}
      <Navbar
        currentView={currentView}
        setView={setView}
        onOpenFailureModal={() => setIsFailureModalOpen(true)}
        activeNegotiationId={activeNegotiationId}
      />

      {/* Main View Router */}
      <main className="flex-1 pb-16">
        {currentView === 'buyer' && (
          <BuyerView 
            onStartNegotiation={handleStartNegotiation} 
          />
        )}

        {currentView === 'negotiation' && (
          <NegotiationView
            negotiationId={activeNegotiationId}
            onProceedToPayment={handleProceedToPayment}
            onInspectOffer={handleInspectOffer}
          />
        )}

        {currentView === 'payment' && (
          <PaymentView
            orderId={activeOrderId}
            onPaymentComplete={handlePaymentComplete}
          />
        )}

        {currentView === 'order' && (
          <OrderView
            orderId={activeOrderId}
            onStartNew={handleStartNew}
            onInspectAudit={() => setView('audit')}
          />
        )}

        {currentView === 'merchant' && (
          <MerchantDashboardView
            setView={setView}
            onSelectNegotiation={(negId) => {
              setActiveNegotiationId(negId);
              setView('negotiation');
            }}
          />
        )}

        {currentView === 'products' && <ProductsView />}

        {currentView === 'policies' && <PoliciesView />}

        {currentView === 'inventory' && <InventoryView />}

        {currentView === 'analytics' && <AnalyticsView />}

        {currentView === 'audit' && (
          <AuditView selectedOfferId={selectedOfferIdForAudit} />
        )}

        {currentView === 'simulation' && <SimulationView />}
      </main>

      {/* Global Failure Injection Modal ("BREAK THE AGENT") */}
      <FailureInjectionModal
        isOpen={isFailureModalOpen}
        onClose={() => setIsFailureModalOpen(false)}
        activeNegotiationId={activeNegotiationId}
        activeOrderId={activeOrderId}
      />

      {/* Footer */}
      <footer className="border-t border-fintech-cardBorder/60 py-6 px-4 text-center text-xs text-slate-500 bg-[#0c1018]/50">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>AI AGENT NEGOTIATOR • Track: AI Growth & Agentic Commerce</span>
          <span className="font-mono text-[11px] text-slate-400">Deterministic Fintech Engine & Razorpay Sandbox Protected</span>
        </div>
      </footer>

    </div>
  );
}
