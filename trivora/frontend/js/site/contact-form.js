// Contact form: validates, then sends the enquiry to the backend (POST /api/contact).
import { request, ApiError } from '../api.js';

export function initContactForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;

  const status = document.getElementById('formStatus');
  const button = document.getElementById('formBtn');
  const field = (name) => form.querySelector(`[name="${name}"]`);

  const setStatus = (message, kind = '') => {
    status.textContent = message;
    status.className = 'form-status' + (kind ? ' ' + kind : '');
  };

  // Pricing-card buttons pre-select the matching service in the form.
  document.querySelectorAll('[data-service]').forEach((btn) => {
    btn.addEventListener('click', () => { field('service').value = btn.dataset.service; });
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    form.querySelectorAll('.invalid').forEach((el) => el.classList.remove('invalid'));
    setStatus('');

    const payload = Object.fromEntries(new FormData(form).entries());

    // quick checks in the browser (the backend validates again)
    const problems = [];
    if ((payload.name || '').trim().length < 2) problems.push(['name', 'Please enter your name.']);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test((payload.email || '').trim())) problems.push(['email', 'Please enter a valid email address.']);
    if ((payload.message || '').trim().length < 10) problems.push(['message', 'Please tell us a little more about your project.']);
    if (problems.length) {
      problems.forEach(([name]) => field(name).classList.add('invalid'));
      setStatus(problems[0][1], 'err');
      return;
    }

    const label = button.textContent;
    button.disabled = true;
    button.textContent = 'Sending...';
    try {
      const data = await request('/api/contact', { method: 'POST', body: payload });
      form.reset();
      setStatus(data.message || 'Thank you! We will be in touch shortly.', 'ok');
    } catch (err) {
      const errors = err instanceof ApiError ? err.data.errors : null;
      if (errors) Object.keys(errors).forEach((name) => field(name)?.classList.add('invalid'));
      setStatus(err.message || 'Something went wrong. Please try again or call us.', 'err');
    } finally {
      button.disabled = false;
      button.textContent = label;
    }
  });
}
