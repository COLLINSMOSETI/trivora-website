# Trivora Technologies - Website

Website for **Trivora Technologies** (websites, systems integration and apps), split into two
separate parts that talk to each other only through a small API:

| | |
|---|---|
| Email | trivoratechnologies1@gmail.com |
| Phones | 0703502267, +254 116 918656, +254 112 061280 |
| Headline offer | Website development from **KSh 30,000** |

```
trivora/
├── frontend/                     WHAT VISITORS SEE (plain HTML, CSS, JavaScript - no build step)
│   ├── index.html                The public website
│   ├── robots.txt
│   ├── admin/
│   │   ├── login.html            Admin sign-in page
│   │   └── index.html            Admin dashboard
│   ├── css/
│   │   ├── theme.css             Colours, fonts, animated blue background, buttons (shared)
│   │   ├── site.css              Public website styles
│   │   └── admin.css             Admin dashboard styles
│   └── js/
│       ├── config.js             THE connection to the backend (one line: API_BASE)
│       ├── api.js                Shared helper that calls the backend
│       ├── site/                 Public website scripts
│       │   ├── main.js           Starts everything below
│       │   ├── nav.js            Sticky menu + mobile menu
│       │   ├── reveal.js         Fade-in on scroll
│       │   ├── network-bg.js     Animated dots-and-lines background
│       │   ├── contact-form.js   Sends the contact form  ->  POST /api/contact
│       │   └── tracker.js        Records a visit            ->  POST /api/track
│       └── admin/                Admin dashboard scripts
│           ├── login.js          Sign in                    ->  POST /api/admin/login
│           ├── dashboard.js      Starts the dashboard, tabs, sign-out
│           ├── helpers.js        Shared utilities (escaping, dates, toasts)
│           ├── overview.js       Totals + chart             ->  GET  /api/admin/stats
│           ├── enquiries.js      Enquiry list + export      ->  GET  /api/admin/enquiries
│           ├── enquiry-modal.js  View / status / notes      ->  PATCH, DELETE /api/admin/enquiries/<id>
│           ├── visitors.js       Visitor log + export       ->  GET  /api/admin/visitors
│           └── settings.js       Change password            ->  POST /api/admin/password
│
├── backend/                      THE SERVER AND DATABASE (Python / Flask)
│   ├── run.py                    Start here:  python run.py
│   ├── requirements.txt          Python packages
│   ├── Procfile                  For hosts like Render / Railway
│   ├── .env.example              Settings template (copy to .env)
│   ├── data/                     Created automatically: trivora.db (database) + secret key
│   └── server/
│       ├── __init__.py           Builds the app and plugs everything together
│       ├── config.py             ALL settings (company details, services, email, CORS ...)
│       ├── schema.sql            Database tables (admins, enquiries, visitors)
│       ├── database.py           Database connection + first admin account
│       ├── security.py           Admin tokens, rate limiting, CORS, security headers
│       ├── utils.py              Input cleaning, browser detection, CSV export
│       ├── mailer.py             Email notifications
│       └── routes/
│           ├── public.py         /api/contact, /api/track, /api/health   (no sign-in)
│           ├── auth.py           /api/admin/login, /me, /password
│           ├── admin.py          /api/admin/stats, /enquiries, /visitors, /export/*
│           └── frontend.py       Optional: serves ../frontend so one command runs everything
│
└── README.md
```

## How the two parts are connected

```
 Visitor's browser                                  Your server
 ┌────────────────────────┐   JSON over HTTP   ┌──────────────────────────┐
 │ frontend/              │  ───────────────▶  │ backend/                 │
 │  js/config.js (API_BASE)│  /api/contact      │  routes -> SQLite        │
 │  js/api.js              │  /api/track        │  (data/trivora.db)       │
 │  js/site/*  js/admin/*  │  /api/admin/...    │  emails via Gmail        │
 └────────────────────────┘  ◀───────────────  └──────────────────────────┘
```

- The frontend never touches the database; it only calls the API listed above.
- The only link between the folders is `frontend/js/config.js` (where the API lives) and, if hosted
  separately, `CORS_ORIGINS` in `backend/.env` (which websites may call the API).
- Admin sign-in returns a signed token. The dashboard sends it with each request and keeps it in
  `sessionStorage`, so it is forgotten when the tab closes and expires after 8 hours. Changing the
  password signs every device out.

## 1. Run it on your computer

You need Python 3.9 or newer.

```bash
cd trivora/backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
python run.py
```

- Website: http://localhost:5000/
- Admin dashboard: http://localhost:5000/admin/

Open the site through this address, **not** by double-clicking `index.html` (browsers block the scripts
and API calls on `file://`).

**Admin password:** the first start creates the admin account. If `ADMIN_PASSWORD` in `.env` is empty,
a random password is printed in the terminal **once** - copy it. Better: set `ADMIN_USERNAME` and
`ADMIN_PASSWORD` in `.env` *before* the first run. Change it later under **Settings** in the dashboard.

## 2. The dashboard (who contacted you / who visited)

- **Overview** - totals, today's numbers, 14-day chart, enquiries by service, visitors by device
- **Enquiries** - search, filter by status, open any enquiry, set status (New / Contacted / In progress / Won / Closed),
  add private notes, reply by email, call, delete, export CSV
- **Visitors** - time, IP address, device, browser, operating system and where each visitor came from (bots hidden by default), export CSV
- **Settings** - change password; shows the company details the backend uses

Times are shown in East Africa Time. The data lives in `backend/data/trivora.db` (SQLite - open it with
*DB Browser for SQLite* if you want to look at the raw tables). **Back it up regularly**, or use the Export CSV buttons.

A repeat visit from the same person within 30 minutes is counted once. Visitors that identify as bots/crawlers
(including headless test browsers) are stored but hidden unless you tick "Show bots".

## 3. Email notifications

Enquiries are **always saved**. To also get an email at trivoratechnologies1@gmail.com for each one:

1. Sign in to the trivoratechnologies1@gmail.com Google account and turn on **2-Step Verification**.
2. Google Account -> Security -> **App passwords** -> create one called "Trivora website" and copy the 16-character code.
3. In `backend/.env` set `SMTP_PASSWORD=` to that code and restart.

You get an email per enquiry (replying goes straight to the customer) and the customer receives an automatic
"we received your request" reply (turn off with `SEND_AUTOREPLY=0`). Never use your normal Gmail password, and never share `.env`.

## 4. Putting it online - two ways

**A. One server (simplest).** Host the whole `trivora` folder on a Python host (Render, Railway, PythonAnywhere, a VPS).
In `backend/`: install `requirements.txt`, start with `gunicorn run:app` (the `Procfile` does this).
The backend also serves the frontend, so nothing else is needed (`SERVE_FRONTEND=1`, the default).

**B. Frontend and backend on different hosts.**
1. Backend: set `SERVE_FRONTEND=0` and `CORS_ORIGINS=https://your-website.com` in its environment.
2. Frontend: upload the `frontend/` folder to any static host (Netlify, cPanel, GitHub Pages...).
3. Edit `frontend/js/config.js`: `export const API_BASE = 'https://api.your-domain.com';`

Either way, on a live site also set: `TRUST_PROXY=1` (so real visitor IPs are logged), a strong `ADMIN_PASSWORD`,
`SMTP_PASSWORD`, and a long random `SECRET_KEY`. Use a **persistent disk** and point `TRIVORA_DATA_DIR`
(or `TRIVORA_DB`) at it, otherwise the database can be wiped when the host redeploys.

## 5. Editing the site

| To change | Edit |
|---|---|
| Text, services, prices, FAQ, phone numbers / email shown on the page | `frontend/index.html` |
| Phone numbers / email used in emails and the dashboard Settings tab | `backend/server/config.py` (`COMPANY`) |
| Colours, fonts, background animation | `frontend/css/theme.css` |
| Public page layout | `frontend/css/site.css` |
| Services offered in the contact form | the `<select name="service">` in `frontend/index.html` **and** `SERVICES` in `backend/server/config.py` (the keys must match) |
| Where the frontend finds the backend | `frontend/js/config.js` |
| Database tables | `backend/server/schema.sql` |

The company details exist in two places (the public page and the backend) because the two parts are independent - keep them in step.
Only the Starter plan shows a price (KSh 30,000); the other plans say "Get a quote".

## 6. Security built in

- Admin API needs a signed, expiring token; sign-in attempts are rate-limited; passwords are stored hashed.
- Contact form: server-side validation, hidden spam field, and a limit of 5 submissions per hour per IP.
- All database queries are parameterised (no SQL injection); the dashboard escapes all customer text.
- CORS only allows the websites you list; security headers and a Content-Security-Policy are sent; CSV exports are protected against spreadsheet formula injection.
- Backend source files are not reachable from the browser (only the `frontend/` folder is served).

**Privacy note:** the site stores visitor IP addresses and enquiry details. If you operate in Kenya, consider adding a short
privacy notice and keeping data only as long as needed (Data Protection Act, 2019).

## 7. What was tested

Backend API (valid/invalid enquiries, spam field, visit tracking, login, wrong password, forged token, status updates,
CSV export, CORS) and, in a real browser: the contact form, admin sign-in/sign-out, dashboard tabs, enquiry editing, CSV download -
both with the backend serving the frontend, and with the frontend hosted on a different address from an API-only backend.
Email sending needs your Gmail app password, so it was not tested.
