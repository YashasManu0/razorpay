const API_BASE = '/api';

export async function fetchMerchants() {
  const res = await fetch(`${API_BASE}/merchants/`);
  return res.json();
}

export async function fetchMerchantDashboard(merchantId) {
  const res = await fetch(`${API_BASE}/merchants/${merchantId}/dashboard`);
  return res.json();
}

export async function fetchProducts(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/products/?${query}`);
  return res.json();
}

export async function searchProducts(q) {
  const res = await fetch(`${API_BASE}/products/search?q=${encodeURIComponent(q)}`);
  return res.json();
}

export async function syncRealWorldProducts(merchantId = null) {
  const url = merchantId ? `${API_BASE}/products/sync-real-world?merchant_id=${merchantId}` : `${API_BASE}/products/sync-real-world`;
  const res = await fetch(url, { method: 'POST' });
  return res.json();
}

export async function searchRealWorldProducts(q) {
  const res = await fetch(`${API_BASE}/products/real-world/search?q=${encodeURIComponent(q)}`);
  return res.json();
}

export async function fetchInventory(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/inventory/?${query}`);
  return res.json();
}

export async function updateInventory(inventoryId, payload) {
  const res = await fetch(`${API_BASE}/inventory/${inventoryId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function fetchPolicy(merchantId) {
  const url = merchantId ? `${API_BASE}/policies/?merchant_id=${merchantId}` : `${API_BASE}/policies/`;
  const res = await fetch(url);
  return res.json();
}

export async function updatePolicy(policyId, payload) {
  const res = await fetch(`${API_BASE}/policies/${policyId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function listNegotiations(params = {}) {
  const query = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/negotiations/?${query}`);
  return res.json();
}

export async function startNegotiation(payload) {
  const res = await fetch(`${API_BASE}/negotiations/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to start negotiation');
  }
  return res.json();
}

export async function sendNegotiationMessage(negotiationId, payload) {
  const res = await fetch(`${API_BASE}/negotiations/${negotiationId}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    let errMsg = 'Failed to send message';
    try {
      const err = await res.json();
      errMsg = err.detail || errMsg;
    } catch {
      const text = await res.text();
      errMsg = text || errMsg;
    }
    throw new Error(errMsg);
  }
  return res.json();
}

export async function fetchNegotiationDetails(negotiationId) {
  const res = await fetch(`${API_BASE}/negotiations/${negotiationId}`);
  if (!res.ok) {
    let errMsg = 'Failed to fetch details';
    try {
      const err = await res.json();
      errMsg = err.detail || errMsg;
    } catch {
      const text = await res.text();
      errMsg = text || errMsg;
    }
    throw new Error(errMsg);
  }
  return res.json();
}

export async function createPaymentSession(payload, customHeaders = {}) {
  const res = await fetch(`${API_BASE}/payments/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...customHeaders },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to create payment session');
  }
  return res.json();
}

export async function simulatePaymentSuccess(payload) {
  const res = await fetch(`${API_BASE}/payments/simulate-success`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function verifyClientPayment(payload) {
  const res = await fetch(`${API_BASE}/payments/verify-client`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Payment verification failed');
  }
  return res.json();
}

export async function fetchPaymentStatus(orderId) {
  const res = await fetch(`${API_BASE}/payments/${orderId}/status`);
  return res.json();
}

export async function fetchAnalytics(merchantId) {
  const url = merchantId ? `${API_BASE}/analytics/?merchant_id=${merchantId}` : `${API_BASE}/analytics/`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchOfferExplanation(offerId) {
  const res = await fetch(`${API_BASE}/audit/explain/${offerId}`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to fetch audit explanation');
  }
  return res.json();
}

export async function fetchAuditLogs(entityType) {
  const url = entityType ? `${API_BASE}/audit/logs?entity_type=${entityType}` : `${API_BASE}/audit/logs`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchFailureScenarios() {
  const res = await fetch(`${API_BASE}/failure-injection/scenarios`);
  return res.json();
}

export async function triggerFailureScenario(payload) {
  const res = await fetch(`${API_BASE}/failure-injection/trigger`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function fetchSimulationState() {
  const res = await fetch(`${API_BASE}/simulation/state`);
  return res.json();
}

export async function runBanditSimulation(nTrials = 100, resetBandit = false) {
  const res = await fetch(`${API_BASE}/simulation/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ n_trials: nTrials, reset_bandit: resetBandit })
  });
  return res.json();
}
