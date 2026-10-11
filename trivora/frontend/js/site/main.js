// Entry point for the public website (loaded by index.html).
import { initNav } from './nav.js';
import { initReveal } from './reveal.js';
import { initNetworkBackground } from './network-bg.js';
import { initContactForm } from './contact-form.js';
import { trackVisit } from './tracker.js';

const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

initNav();
initReveal();
initNetworkBackground();
initContactForm();
trackVisit();
