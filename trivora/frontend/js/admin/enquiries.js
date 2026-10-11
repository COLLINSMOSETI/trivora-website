// Enquiries tab: searchable, filterable list (GET /api/admin/enquiries) + CSV export.
import { request, download } from '../api.js';
import { $, $$, esc, fmt, serviceLabel, statusLabel, toast } from './helpers.js';
import { openEnquiry } from './enquiry-modal.js';

let items = [];

export async function loadEnquiries() {
  const params = new URLSearchParams({ limit: '300' });
  const q = $('#enqSearch').value.trim();
  const status = $('#enqStatus').value;
  if (q) params.set('q', q);
  if (status) params.set('status', status);

  try {
    const data = await request('/api/admin/enquiries?' + params, { auth: true });
    items = data.items;
    const body = $('#enqBody');
    if (!items.length) {
      body.innerHTML = '<tr><td colspan="7" class="empty">No enquiries found.</td></tr>';
    } else {
      body.innerHTML = items
        .map(
          (e) => `<tr class="row-click" data-id="${e.id}">
            <td>${e.id}</td>
            <td class="nowrap">${esc(fmt(e.created_at))}</td>
            <td><strong>${esc(e.name)}</strong></td>
            <td>${esc(e.email)}<small>${esc(e.phone || '')}</small></td>
            <td>${esc(serviceLabel(e.service))}<small>${esc(e.budget || '')}</small></td>
            <td><span class="pill ${esc(e.status)}">${esc(statusLabel(e.status))}</span></td>
            <td class="nowrap"><button class="link-btn" type="button">Open</button></td></tr>`
        )
        .join('');
      $$('tr.row-click', body).forEach((tr) =>
        tr.addEventListener('click', () => openEnquiry(items.find((x) => String(x.id) === tr.dataset.id)))
      );
    }
    $('#enqCount').textContent = `${data.total} enquir${data.total === 1 ? 'y' : 'ies'}`;
  } catch (err) {
    if (err.status !== 401) toast(err.message, true);
  }
}

export function initEnquiries() {
  let timer;
  $('#enqSearch').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(loadEnquiries, 300); });
  $('#enqStatus').addEventListener('change', loadEnquiries);
  $('#exportEnquiries').addEventListener('click', () =>
    download('/api/admin/export/enquiries.csv', 'trivora-enquiries.csv').catch((e) => toast(e.message, true))
  );
}
