// Settings tab: backend company details + change password (POST /api/admin/password).
import { request, token } from '../api.js';
import { $, esc, state, toast } from './helpers.js';

export function initSettings() {
  const c = state.company;
  $('#companyDetails').innerHTML = `
    <dt>Email</dt><dd>${esc(c.email)}</dd>
    <dt>Phones</dt><dd>${(c.phones || []).map((p) => esc(p.display)).join('<br>')}</dd>
    <dt>Starting price</dt><dd>KSh ${Number(c.starting_price || 0).toLocaleString('en-KE')} (website development)</dd>`;

  $('#pwForm').addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const form = ev.target;
    try {
      await request('/api/admin/password', {
        method: 'POST',
        auth: true,
        body: { current: form.current.value, new: form.new.value },
      });
      form.reset();
      toast('Password updated. Signing you out...');
      // the backend invalidates old tokens when the password changes
      setTimeout(() => { token.clear(); location.replace('login.html'); }, 1200);
    } catch (err) { toast(err.message, true); }
  });
}
