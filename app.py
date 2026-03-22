import os
import requests
from flask import Flask, request, redirect, url_for

app = Flask(__name__)

MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL", "")
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE   = os.environ.get("AIRTABLE_TABLE", "Leads")

# ── HTML templates (inline so it's one-file simple) ───────────────────────────

FORM_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Get Early Access</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0f0f11;
    color: #e8e8ec;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }
  .card {
    background: #18181b;
    border: 1px solid #27272a;
    border-radius: 16px;
    padding: 2.5rem;
    width: 100%;
    max-width: 460px;
  }
  .badge {
    display: inline-block;
    background: #1a1a2e;
    color: #818cf8;
    border: 1px solid #3730a3;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.3rem 0.75rem;
    border-radius: 99px;
    margin-bottom: 1.25rem;
  }
  h1 { font-size: 1.6rem; font-weight: 700; line-height: 1.3; margin-bottom: 0.6rem; }
  p  { font-size: 0.92rem; color: #71717a; line-height: 1.6; margin-bottom: 1.8rem; }
  label {
    display: block;
    font-size: 0.8rem;
    font-weight: 500;
    color: #a1a1aa;
    margin-bottom: 0.35rem;
  }
  input, select {
    width: 100%;
    background: #09090b;
    border: 1px solid #27272a;
    border-radius: 8px;
    color: #e8e8ec;
    font-size: 0.9rem;
    padding: 0.65rem 0.9rem;
    margin-bottom: 1rem;
    outline: none;
    transition: border-color 0.15s;
  }
  input:focus, select:focus { border-color: #6366f1; }
  select option { background: #18181b; }
  button {
    width: 100%;
    background: #6366f1;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 600;
    padding: 0.8rem;
    cursor: pointer;
    transition: background 0.15s;
    margin-top: 0.25rem;
  }
  button:hover { background: #4f46e5; }
  .footnote { font-size: 0.75rem; color: #52525b; text-align: center; margin-top: 1rem; }
  {% if error %}
  .error-banner {
    background: #1c0a0a; border: 1px solid #7f1d1d; color: #fca5a5;
    border-radius: 8px; padding: 0.7rem 1rem; font-size: 0.85rem; margin-bottom: 1rem;
  }
  {% endif %}
</style>
</head>
<body>
<div class="card">
  <span class="badge">Early Access</span>
  <h1>Join the waitlist</h1>
  <p>We'll email you the moment spots open up. No spam — one email, that's it.</p>

  {% if error %}
  <div class="error-banner">Something went wrong. Please try again.</div>
  {% endif %}

  <form action="/submit" method="POST">
    <label for="name">Full name</label>
    <input id="name" name="name" type="text" placeholder="Jane Smith" required>

    <label for="email">Work email</label>
    <input id="email" name="email" type="email" placeholder="jane@company.com" required>

    <label for="role">Your role</label>
    <select id="role" name="role" required>
      <option value="" disabled selected>Select your role…</option>
      <option>Founder / CEO</option>
      <option>Product Manager</option>
      <option>Engineer</option>
      <option>Designer</option>
      <option>Marketing</option>
      <option>Operations</option>
      <option>Other</option>
    </select>

    <button type="submit">Request access →</button>
  </form>
  <p class="footnote">No credit card. No commitment.</p>
</div>
</body>
</html>
"""

THANKS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>You're on the list</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0f0f11; color: #e8e8ec;
    min-height: 100vh; display: flex;
    align-items: center; justify-content: center; padding: 2rem;
  }
  .card {
    background: #18181b; border: 1px solid #27272a;
    border-radius: 16px; padding: 2.5rem;
    width: 100%; max-width: 420px; text-align: center;
  }
  .icon { font-size: 2.5rem; margin-bottom: 1rem; }
  h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.6rem; }
  p  { font-size: 0.92rem; color: #71717a; line-height: 1.6; }
  a  { color: #6366f1; text-decoration: none; font-size: 0.85rem; display: inline-block; margin-top: 1.5rem; }
</style>
</head>
<body>
<div class="card">
  <div class="icon">✅</div>
  <h1>You're on the list</h1>
  <p>Check your inbox — a confirmation just landed. We'll reach out when your spot opens up.</p>
  <a href="/">← Submit another</a>
</div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Leads Dashboard</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0f0f11; color: #e8e8ec;
    min-height: 100vh; padding: 2rem;
  }
  h1 { font-size: 1.4rem; font-weight: 700; margin-bottom: 0.3rem; }
  .sub { font-size: 0.85rem; color: #71717a; margin-bottom: 2rem; }
  .count {
    display: inline-block;
    background: #1a1a2e; color: #818cf8;
    border: 1px solid #3730a3;
    border-radius: 99px; font-size: 0.8rem;
    font-weight: 600; padding: 0.2rem 0.65rem;
    margin-left: 0.5rem; vertical-align: middle;
  }
  table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
  th {
    text-align: left; padding: 0.65rem 1rem;
    color: #71717a; font-weight: 500;
    border-bottom: 1px solid #27272a;
    font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em;
  }
  td { padding: 0.75rem 1rem; border-bottom: 1px solid #1c1c1f; }
  tr:last-child td { border-bottom: none; }
  .pill {
    display: inline-block;
    background: #18181b; border: 1px solid #27272a;
    border-radius: 6px; font-size: 0.75rem;
    padding: 0.2rem 0.55rem; color: #a1a1aa;
  }
  .error { color: #f87171; font-size: 0.9rem; padding: 1rem 0; }
  .empty { color: #52525b; font-size: 0.9rem; padding: 2rem 0; text-align: center; }
</style>
</head>
<body>
<h1>Waitlist leads <span class="count">{{ count }}</span></h1>
<p class="sub">Live from Airtable · refresh to update</p>

{% if error %}
  <p class="error">{{ error }}</p>
{% elif leads %}
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Role</th>
        <th>Submitted</th>
      </tr>
    </thead>
    <tbody>
    {% for lead in leads %}
      <tr>
        <td>{{ lead.name }}</td>
        <td>{{ lead.email }}</td>
        <td><span class="pill">{{ lead.role }}</span></td>
        <td>{{ lead.created }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
{% else %}
  <p class="empty">No leads yet. Submit the form to see them appear here.</p>
{% endif %}
</body>
</html>
"""

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    from jinja2 import Template
    return Template(FORM_PAGE).render(error=False)

@app.route("/submit", methods=["POST"])
def submit():
    payload = {
        "name":  request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "role":  request.form.get("role", "").strip(),
    }

    # Fire the Make webhook (non-blocking best-effort)
    if MAKE_WEBHOOK_URL:
        try:
            requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=5)
        except requests.RequestException:
            pass  # Make is best-effort; don't block the user

    from jinja2 import Template
    return Template(THANKS_PAGE).render()

@app.route("/leads")
def leads():
    """Pull records straight from Airtable and display them."""
    from jinja2 import Template

    records, error = [], None

    if not all([AIRTABLE_API_KEY, AIRTABLE_BASE_ID]):
        error = "Airtable env vars not set. Add AIRTABLE_API_KEY and AIRTABLE_BASE_ID."
    else:
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE}"
        headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
        params  = {"maxRecords": 100}

        try:
            r = requests.get(url, headers=headers, params=params, timeout=8)
            r.raise_for_status()
            for rec in r.json().get("records", []):
                f = rec.get("fields", {})
                records.append({
                    "name":    f.get("Name", "—"),
                    "email":   f.get("Email", "—"),
                    "role":    f.get("Role", "—"),
                    "created": rec.get("createdTime", "")[:10],
                })
        except requests.RequestException as exc:
            error = f"Airtable fetch failed: {exc}"

    return Template(DASHBOARD_PAGE).render(leads=records, count=len(records), error=error)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
