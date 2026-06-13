# Test Report

Static tests run in this environment:

- Python compile test: `python -m py_compile bot.py app.py railway_start.py` — PASS
- Template block balance check for all templates — PASS
- Dashboard link/form route coverage check — PASS
- Secret scan for real-looking Discord token / Mongo URI in final repo — PASS

Not run here:

- Live Discord bot login, because it requires a real bot token.
- Live MongoDB reads/writes, because it requires your MongoDB URI.
- Browser microphone / Railway public WebSocket, because it requires deployed Railway networking.

After Railway deploy, verify:

1. `/healthz` returns OK.
2. Dashboard login works.
3. `/setup_tickets` sends the ticket panel.
4. `/setup_roles` sends the role panel.
5. Welcome message triggers when a test account joins.
6. Security toggles save from dashboard and affect bot behavior.
