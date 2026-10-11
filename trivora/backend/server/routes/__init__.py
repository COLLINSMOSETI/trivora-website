"""HTTP routes, one module per concern:

public.py    - what the website calls (contact form, visit tracking, health check)
auth.py      - admin sign-in, "who am I", change password
admin.py     - dashboard data (stats, enquiries, visitors, CSV exports)
frontend.py  - optional: serves the ../frontend folder so one command runs everything
"""
