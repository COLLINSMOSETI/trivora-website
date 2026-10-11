// Small shared utilities for the admin dashboard.

export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

/** Escape text before putting it into innerHTML (prevents script injection from customer input). */
export const esc = (value) =>
  String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// The backend stores UTC; show East Africa Time.
const toDate = (s) => new Date(String(s).replace(' ', 'T') + 'Z');
export const fmt = (s) =>
  toDate(s).toLocaleString('en-KE', { timeZone: 'Africa/Nairobi', day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });

/** Labels come from the backend (GET /api/admin/me) so both sides always agree. */
export const state = { services: {}, statuses: [], company: {} };
export const serviceLabel = (key) => state.services[key] || key;
export const statusLabel = (s) => String(s).replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase());

export function fillStatusOptions(select, withAll = false) {
  select.innerHTML = '';
  if (withAll) select.add(new Option('All statuses', ''));
  state.statuses.forEach((s) => select.add(new Option(statusLabel(s), s)));
}

let toastTimer;
export function toast(message, isError = false) {
  const el = $('#toast');
  el.textContent = message;
  el.className = 'toast show' + (isError ? ' err' : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = 'toast'; }, 3200);
}
