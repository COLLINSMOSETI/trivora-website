// Entry point for the admin dashboard (frontend/admin/index.html).
// Checks the sign-in, loads labels from the backend, then wires up each tab's module.
import { request, token } from '../api.js';
import { $, $$, state, fillStatusOptions, toast } from './helpers.js';
import { loadOverview, refreshBadge } from './overview.js';
import { initEnquiries, loadEnquiries } from './enquiries.js';
import { initVisitors, loadVisitors } from './visitors.js';
import { initSettings } from './settings.js';
import { initModal } from './enquiry-modal.js';

const TABS = ['overview', 'enquiries', 'visitors', 'settings'];

function showTab(name) {
  $$('.tab').forEach((b) => b.classList.toggle('active', b.dataset.tab === name));
  $$('.panel').forEach((p) => p.classList.toggle('active', p.id === 'tab-' + name));
  if (name === 'overview') loadOverview();
  if (name === 'enquiries') loadEnquiries();
  if (name === 'visitors') loadVisitors(true);
  history.replaceState(null, '', '#' + name);
}

const activeTab = () => $('.tab.active').dataset.tab;

async function start() {
  let me;
  try {
    me = await request('/api/admin/me', { auth: true }); // 401 -> sent back to login.html
  } catch (err) {
    if (err.status !== 401) {
      document.body.classList.remove('pending');
      toast(err.message, true);
    }
    return;
  }

  Object.assign(state, me.meta);
  $('#adminName').textContent = me.admin.username;
  fillStatusOptions($('#enqStatus'), true);
  fillStatusOptions($('#mStatus'));
  document.body.classList.remove('pending');

  initModal();
  initEnquiries();
  initVisitors();
  initSettings();

  $$('.tab').forEach((b) => b.addEventListener('click', () => showTab(b.dataset.tab)));
  $$('[data-goto]').forEach((b) => b.addEventListener('click', () => showTab(b.dataset.goto)));
  $('#logoutBtn').addEventListener('click', () => {
    token.clear();
    location.replace('login.html');
  });

  // an enquiry was saved or deleted in the modal -> refresh what is on screen
  document.addEventListener('enquiry:changed', () => {
    if (activeTab() === 'overview') loadOverview();
    else { loadEnquiries(); refreshBadge(); }
  });

  const initial = (location.hash || '#overview').slice(1);
  showTab(TABS.includes(initial) ? initial : 'overview');
  setInterval(() => { if (!document.hidden && activeTab() === 'overview') loadOverview(); }, 60000);
}

if (token.get()) start();
else location.replace('login.html');
