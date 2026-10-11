// Enquiry detail pop-up: view everything, change status, add notes, reply, call or delete
// (PATCH / DELETE /api/admin/enquiries/<id>). Tells the rest of the dashboard via an "enquiry:changed" event.
import { request } from '../api.js';
import { $, esc, fmt, serviceLabel, toast } from './helpers.js';

let current = null;

const changed = () => document.dispatchEvent(new CustomEvent('enquiry:changed'));

function close() {
  $('#modal').hidden = true;
  current = null;
}

export function openEnquiry(e) {
  if (!e) return;
  current = e;
  $('#mTitle').textContent = `Enquiry #${e.id} - ${e.name}`;
  $('#mDetails').innerHTML = `
    <dt>Received</dt><dd>${esc(fmt(e.created_at))}</dd>
    <dt>Name</dt><dd>${esc(e.name)}</dd>
    <dt>Email</dt><dd><a href="mailto:${esc(e.email)}">${esc(e.email)}</a></dd>
    <dt>Phone</dt><dd>${e.phone ? `<a href="tel:${esc(e.phone)}">${esc(e.phone)}</a>` : '-'}</dd>
    <dt>Service</dt><dd>${esc(serviceLabel(e.service))}</dd>
    <dt>Budget</dt><dd>${esc(e.budget || '-')}</dd>
    <dt>IP</dt><dd>${esc(e.ip || '-')}</dd>
    <dt>Email sent</dt><dd>${e.notified ? 'Yes' : 'No / not configured'}</dd>`;
  $('#mMessage').textContent = e.message;
  $('#mStatus').value = e.status;
  $('#mNotes').value = e.notes || '';
  $('#mReply').href = `mailto:${e.email}?subject=${encodeURIComponent('Re: your Trivora enquiry')}`;
  const call = $('#mCall');
  call.hidden = !e.phone;
  call.href = e.phone ? 'tel:' + e.phone.replace(/[^0-9+]/g, '') : '#';
  $('#modal').hidden = false;
}

export function initModal() {
  const modal = $('#modal');
  $('#mClose').addEventListener('click', close);
  modal.addEventListener('click', (ev) => { if (ev.target === modal) close(); });
  document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape' && !modal.hidden) close(); });

  $('#mSave').addEventListener('click', async () => {
    if (!current) return;
    try {
      await request(`/api/admin/enquiries/${current.id}`, {
        method: 'PATCH',
        auth: true,
        body: { status: $('#mStatus').value, notes: $('#mNotes').value },
      });
      toast('Saved');
      close();
      changed();
    } catch (err) { toast(err.message, true); }
  });

  $('#mDelete').addEventListener('click', async () => {
    if (!current || !confirm(`Delete enquiry #${current.id} from ${current.name}? This cannot be undone.`)) return;
    try {
      await request(`/api/admin/enquiries/${current.id}`, { method: 'DELETE', auth: true });
      toast('Deleted');
      close();
      changed();
    } catch (err) { toast(err.message, true); }
  });
}
