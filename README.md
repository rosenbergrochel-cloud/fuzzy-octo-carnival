# Lead Capture — Render + Make + Airtable

Replaces **Typeform** (~$25/mo) and **Mailchimp** (~$13/mo).

## What it does
- `/`        → Waitlist form (your Typeform replacement)
- `/submit`  → Fires a Make webhook with the lead's data
- `/leads`   → Live dashboard pulling directly from Airtable

---

## Deploy to Render

1. Push this folder to a GitHub repo.
2. Go to [render.com](https://render.com) → New → Web Service → connect your repo.
3. Set **Build Command:** `pip install -r requirements.txt`
4. Set **Start Command:** `gunicorn app:app`
5. Add these **Environment Variables:**

| Key | Value |
|-----|-------|
| `MAKE_WEBHOOK_URL` | Your Make custom webhook URL (see below) |
| `AIRTABLE_API_KEY` | Your Airtable personal access token |
| `AIRTABLE_BASE_ID` | e.g. `appXXXXXXXXXXXXXX` |
| `AIRTABLE_TABLE`   | `Leads` (or whatever you name it) |

---

## Airtable Setup

Create a base with a table called **Leads** and these fields:

| Field | Type |
|-------|------|
| Name  | Single line text |
| Email | Email |
| Role  | Single line text |

Get your **Personal Access Token** from: airtable.com/create/tokens
Get your **Base ID** from the Airtable API docs URL for your base.

---

## Make Scenario (3 modules)

```
[Custom Webhook] → [Airtable: Create Record] → [Gmail: Send Email]
```

### Module 1 — Custom Webhook
- Copy the webhook URL → paste into Render env var `MAKE_WEBHOOK_URL`
- Map fields: `name`, `email`, `role`

### Module 2 — Airtable: Create a Record
- Connection: your Airtable account
- Base: your Leads base
- Table: Leads
- Map: Name → `{{name}}`, Email → `{{email}}`, Role → `{{role}}`

### Module 3 — Gmail: Send an Email
- To: `{{email}}`
- Subject: `You're on the list, {{name}}`
- Body:
  > Hey {{name}}, you're officially on the waitlist.
  > We'll reach out when your spot is ready.

---

## Subscriptions Killed

| Tool | Monthly Cost | Replaced By |
|------|-------------|-------------|
| Typeform (basic) | ~$25 | This Render app (free tier) |
| Mailchimp (essentials) | ~$13 | Make + Gmail module (free) |
| **Total saved** | **~$38/mo** | |
