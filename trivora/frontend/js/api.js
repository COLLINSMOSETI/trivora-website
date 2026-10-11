// Shared helper for talking to the Trivora backend (used by the public site AND the admin dashboard).
import { API_BASE } from './config.js';

const TOKEN_KEY = 'trivora_admin_token';

/** Admin sign-in token, kept in sessionStorage so it disappears when the tab is closed. */
export const token = {
  get() { try { return sessionStorage.getItem(TOKEN_KEY) || ''; } catch { return ''; } },
  set(value) { try { sessionStorage.setItem(TOKEN_KEY, value); } catch { /* storage blocked */ } },
  clear() { try { sessionStorage.removeItem(TOKEN_KEY); } catch { /* storage blocked */ } },
};

export class ApiError extends Error {
  constructor(message, status = 0, data = {}) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export const apiUrl = (path) => API_BASE.replace(/\/+$/, '') + path;

function backToLogin() {
  token.clear();
  location.replace(new URL('login.html', location.href).href);
}

/**
 * Call the backend and return the parsed JSON.
 *  auth:     send the admin token
 *  redirect: on 401 go to the login page (turn off on the login page itself)
 */
export async function request(path, { method = 'GET', body, auth = false, redirect = true } = {}) {
  const headers = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (auth && token.get()) headers.Authorization = `Bearer ${token.get()}`;

  let res;
  try {
    res = await fetch(apiUrl(path), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError('Cannot reach the server. Please check your connection.');
  }

  const data = await res.json().catch(() => ({}));
  if (auth && res.status === 401) {
    if (redirect) backToLogin();
    throw new ApiError('Please sign in again.', 401, data);
  }
  if (!res.ok || data.ok === false) throw new ApiError(data.error || 'Request failed.', res.status, data);
  return data;
}

/** Download a protected file (e.g. a CSV export) using the admin token. */
export async function download(path, filename) {
  let res;
  try {
    res = await fetch(apiUrl(path), { headers: token.get() ? { Authorization: `Bearer ${token.get()}` } : {} });
  } catch {
    throw new ApiError('Cannot reach the server. Please check your connection.');
  }
  if (res.status === 401) { backToLogin(); throw new ApiError('Please sign in again.', 401); }
  if (!res.ok) throw new ApiError('Download failed.', res.status);

  const url = URL.createObjectURL(await res.blob());
  const link = Object.assign(document.createElement('a'), { href: url, download: filename });
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
