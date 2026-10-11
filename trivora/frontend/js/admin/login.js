// Admin sign-in page: POST /api/admin/login -> store token -> open the dashboard.
import { request, token } from '../api.js';

const form = document.getElementById('loginForm');
const button = document.getElementById('loginBtn');
const errorBox = document.getElementById('loginError');

const showError = (message) => {
  errorBox.textContent = message;
  errorBox.hidden = !message;
};

// Already signed in? Skip straight to the dashboard.
if (token.get()) {
  request('/api/admin/me', { auth: true, redirect: false })
    .then(() => location.replace('index.html'))
    .catch(() => token.clear());
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  showError('');
  button.disabled = true;
  button.textContent = 'Signing in...';
  try {
    const data = await request('/api/admin/login', {
      method: 'POST',
      body: { username: form.username.value.trim(), password: form.password.value },
    });
    token.set(data.token);
    location.replace('index.html');
  } catch (err) {
    showError(err.message);
    button.disabled = false;
    button.textContent = 'Sign in';
  }
});
