// Overview tab: totals, 14-day chart, breakdowns and latest enquiries (GET /api/admin/stats).
import { request } from '../api.js';
import { $, $$, esc, fmt, serviceLabel, statusLabel, toast } from './helpers.js';
import { openEnquiry } from './enquiry-modal.js';

export function setNewBadge(count) {
  const badge = $('#newCount');
  badge.textContent = count;
  badge.hidden = !count;
}

export async function refreshBadge() {
  try {
    const { stats } = await request('/api/admin/stats', { auth: true });
    setNewBadge(stats.enquiries_new);
  } catch { /* badge is optional */ }
}

export async function loadOverview() {
  try {
    const { stats, series, by_service, by_device } = await request('/api/admin/stats', { auth: true });
    $('#sEnqTotal').textContent = stats.enquiries_total;
    $('#sEnqNew').textContent = stats.enquiries_new;
    $('#sEnqToday').textContent = stats.enquiries_today;
    $('#sVisToday').textContent = stats.visits_today;
    $('#sVisTotal').textContent = stats.visits_total;
    $('#sVisUnique').textContent = stats.unique_visitors;
    setNewBadge(stats.enquiries_new);

    renderChart(series);
    renderBars('#byService', by_service.map((r) => [serviceLabel(r.service), r.count]));
    renderBars('#byDevice', by_device.map((r) => [r.device, r.count]));

    const { items } = await request('/api/admin/enquiries?limit=5', { auth: true });
    const box = $('#recent');
    if (!items.length) {
      box.innerHTML = '<p class="muted">No enquiries yet. They will appear here as soon as someone fills in the contact form.</p>';
      return;
    }
    box.innerHTML = items
      .map(
        (e) => `<div class="recent-item" data-id="${e.id}">
          <div><strong>${esc(e.name)}</strong> <span class="pill ${esc(e.status)}">${esc(statusLabel(e.status))}</span>
          <p>${esc(serviceLabel(e.service))} &mdash; ${esc(e.message)}</p></div>
          <span class="when">${esc(fmt(e.created_at))}</span></div>`
      )
      .join('');
    $$('.recent-item', box).forEach((el) =>
      el.addEventListener('click', () => openEnquiry(items.find((x) => String(x.id) === el.dataset.id)))
    );
  } catch (err) {
    if (err.status !== 401) toast(err.message, true);
  }
}

function renderChart(series) {
  const max = Math.max(1, ...series.map((d) => Math.max(d.visits, d.enquiries)));
  const chart = $('#chart');
  chart.innerHTML = '';
  series.forEach((d) => {
    const col = document.createElement('div');
    col.className = 'col';
    col.title = `${d.date}: ${d.visits} visits, ${d.enquiries} enquiries`;
    col.innerHTML = '<div class="pair"><div class="bar v"></div><div class="bar e"></div></div><span class="lbl"></span>';
    col.querySelector('.lbl').textContent = `${d.date.slice(8)}/${d.date.slice(5, 7)}`;
    chart.appendChild(col);
    requestAnimationFrame(() => {
      col.querySelector('.bar.v').style.height = (d.visits / max) * 100 + '%';
      col.querySelector('.bar.e').style.height = (d.enquiries / max) * 100 + '%';
    });
  });
}

function renderBars(selector, rows) {
  const box = $(selector);
  if (!rows.length) { box.innerHTML = '<p class="muted small">No data yet.</p>'; return; }
  const max = Math.max(...rows.map((r) => r[1]));
  box.innerHTML = rows
    .map(([label, n]) => `<div class="brow"><span>${esc(label)}</span><div class="track"><div class="fill" data-w="${(n / max) * 100}"></div></div><span class="n">${n}</span></div>`)
    .join('');
  $$('.fill', box).forEach((f) => requestAnimationFrame(() => { f.style.width = f.dataset.w + '%'; }));
}
