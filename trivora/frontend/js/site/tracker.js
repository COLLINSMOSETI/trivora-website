// Tells the backend about this visit (POST /api/track) so it shows up in the admin Visitors tab.
import { request } from '../api.js';

const KEY = 'trivora_last_visit';
const THIRTY_MINUTES = 30 * 60 * 1000;

export function trackVisit() {
  try {
    const last = Number(localStorage.getItem(KEY) || 0);
    if (Date.now() - last < THIRTY_MINUTES) return; // already counted recently
    localStorage.setItem(KEY, String(Date.now()));
  } catch { /* storage blocked: the backend de-duplicates anyway */ }

  request('/api/track', {
    method: 'POST',
    body: { path: location.pathname, referrer: document.referrer },
  }).catch(() => { /* tracking must never break the site */ });
}
