from flask import Flask, send_from_directory, jsonify, request
import json
import os
from pathlib import Path

app = Flask(__name__, static_folder='')

BASE = Path(__file__).parent


def load_json_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def gather_businesses():
    results = []
    # load packaged businesses
    packaged = load_json_file(BASE / 'businesses.json') or []
    for b in packaged:
        entry = {
            'name': b.get('name'),
            'category': b.get('category'),
            'phones': [b.get('phone')] if b.get('phone') else [],
            'address': b.get('address',''),
            'website': b.get('website',''),
            'description': b.get('description',''),
            'source': 'packaged'
        }
        results.append(entry)

    # load selenium/facebook results if present (categorized dict)
    for candidate in ('melissa_selenium.json', 'melissa_recs.json', 'fb_recs.json'):
        path = BASE / candidate
        if path.exists():
            data = load_json_file(path)
            if isinstance(data, dict):
                for cat, items in data.items():
                    for it in items:
                        entry = {
                            'name': it.get('name_guess') or it.get('excerpt','')[:80],
                            'category': it.get('category') or cat,
                            'phones': it.get('phones',[]),
                            'address': it.get('address',''),
                            'website': (it.get('urls') or [])[0] if (it.get('urls')) else '',
                            'description': it.get('excerpt',''),
                            'source': candidate
                        }
                        results.append(entry)
            elif isinstance(data, list):
                for it in data:
                    results.append(it)

    return results


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)


@app.route('/api/businesses')
def api_businesses():
    q = request.args.get('q', '').strip().lower()
    category = request.args.get('category', '').strip().lower()
    items = gather_businesses()
    def matches(it):
        if q:
            hay = ' '.join([str(it.get('name','')), str(it.get('description','')), str(it.get('address','')), ' '.join(it.get('phones',[]))]).lower()
            if q not in hay:
                return False
        if category and category != '':
            if category != (it.get('category') or '').lower():
                return False
        return True

    filtered = [it for it in items if matches(it)]
    return jsonify(filtered)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
