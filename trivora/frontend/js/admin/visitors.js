// Visitors tab: who opened the website (GET /api/admin/visitors) + CSV export.
import { request, download } from '../api.js';
import { $, esc, fmt, toast } from './helpers.js';

let offset = 0;

export async function loadVisitors(reset) {
  const body = $('#visBody');
  if (reset) {
    offset = 0;
    body.innerHTML = '<tr><td colspan="6" class="empty">Loading...</td></tr>';
  }
  const bots = $('#showBots').checked ? '1' : '0';
  try {
    const data = await request(`/api/admin/visitors?limit=100&offset=${offset}&bots=${bots}`, { auth: true });
    const rows = data.items
      .map(
        (v) => `<tr><td class="nowrap">${esc(fmt(v.created_at))}</td>
          <td>${esc(v.ip || '-')}${v.is_bot ? ' <span class="pill closed">bot</span>' : ''}</td>
          <td>${esc(v.device || '-')}</td><td>${esc(v.browser || '-')}</td><td>${esc(v.os || '-')}</td>
          <td>${esc(v.referrer || 'Direct')}</td></tr>`
      )
      .join('');
    if (reset) body.innerHTML = rows || '<tr><td colspan="6" class="empty">No visitors recorded yet.</td></tr>';
    else body.insertAdjacentHTML('beforeend', rows);
    offset += data.items.length;
    $('#visCount').textContent = `Showing ${offset} of ${data.total}`;
    $('#visMore').hidden = offset >= data.total;
  } catch (err) {
    if (err.status !== 401) toast(err.message, true);
  }
}

export function initVisitors() {
  $('#visMore').addEventListener('click', () => loadVisitors(false));
  $('#showBots').addEventListener('change', () => loadVisitors(true));
  $('#exportVisitors').addEventListener('click', () =>
    download('/api/admin/export/visitors.csv', 'trivora-visitors.csv').catch((e) => toast(e.message, true))
  );
}
