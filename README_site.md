# Sample City Yellow Pages (demo)

This is a minimal static Yellow Pages-style demo for a city directory.

Files:
- [index.html](index.html) — main page
- [styles.css](styles.css) — styling
- [script.js](script.js) — client-side logic
- [businesses.json](businesses.json) — sample data

To run locally (open in a browser or use a small static server):

```bash
python3 -m http.server 8000
# then open http://localhost:8000 in your browser
```

You can modify `businesses.json` to add, remove, or change entries.

Run with Flask (dynamic API)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
# then open http://localhost:8000
```

The client now fetches businesses from `/api/businesses`. If you have scraped output (e.g. `melissa_selenium.json` or `melissa_recs.json`) place it in the repository root and the server will include those items in the API results.
