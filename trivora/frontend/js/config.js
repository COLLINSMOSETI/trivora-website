// The ONLY place that connects the frontend to the backend.
//
//  ''                          -> backend serves this frontend (python run.py): same address, nothing to set.
//  'https://api.yourdomain.com' -> frontend hosted separately (Netlify, cPanel, GitHub Pages...).
//                                  Put the same address of the frontend in the backend's CORS_ORIGINS.
export const API_BASE = '';
