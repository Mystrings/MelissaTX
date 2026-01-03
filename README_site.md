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

GitHub Pages
-----------

This site can be hosted on GitHub Pages as a static site. The client now falls back to `businesses.json` so the site works without a backend.

Deployment options:

1. Serve from the `main` branch root
	- Go to your repository Settings → Pages → Source, choose `main` branch and `/ (root)`.
	- Wait a minute and open `https://<your-username>.github.io/<repo-name>/`.

2. Serve from the `gh-pages` branch
	- Create a `gh-pages` branch containing the repository files (you can push `main` to `gh-pages` or use an action to deploy).
	- Visit `https://<your-username>.github.io/<repo-name>/`.

Notes:
- To include scraped results, add `melissa_selenium.json` or `melissa_recs.json` to the repository root and push — the site will include those entries because the client falls back to static JSON.
- To automate updates, you can add a GitHub Action that runs a scraper (prefer Graph API) and commits the result JSON to the repo/branch served by Pages; tell me if you want a sample workflow.

