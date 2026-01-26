#!/usr/bin/env python3
"""
Collect GitHub traffic metrics and save to CSV
Run manually: python scripts/collect_metrics.py
"""

import os
import json
import csv
from datetime import datetime
import requests

# Config
REPO = "jojopat/project-reunion"
TOKEN = os.getenv("GITHUB_TOKEN", "")  # For GitHub Actions
OUTPUT_DIR = "metrics"

def get_traffic():
    """Fetch traffic data from GitHub API"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {TOKEN}" if TOKEN else None
    }
    headers = {k: v for k, v in headers.items() if v}
    
    # Get views
    views_url = f"https://api.github.com/repos/{REPO}/traffic/views"
    views_resp = requests.get(views_url, headers=headers)
    views_data = views_resp.json() if views_resp.status_code == 200 else {}
    
    # Get clones
    clones_url = f"https://api.github.com/repos/{REPO}/traffic/clones"
    clones_resp = requests.get(clones_url, headers=headers)
    clones_data = clones_resp.json() if clones_resp.status_code == 200 else {}
    
    return {
        "date": datetime.now().isoformat(),
        "views_total": sum(d.get("count", 0) for d in views_data.get("views", [])),
        "views_unique": sum(d.get("uniques", 0) for d in views_data.get("views", [])),
        "clones_total": sum(d.get("count", 0) for d in clones_data.get("clones", [])),
        "clones_unique": sum(d.get("uniques", 0) for d in clones_data.get("clones", [])),
        "raw_views": views_data,
        "raw_clones": clones_data
    }

def save_metrics(data):
    """Save to CSV and JSON"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Save detailed JSON
    json_file = f"{OUTPUT_DIR}/{today}.json"
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Append to CSV summary
    csv_file = f"{OUTPUT_DIR}/summary.csv"
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'date', 'views_total', 'views_unique', 
            'clones_total', 'clones_unique'
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'date': today,
            'views_total': data['views_total'],
            'views_unique': data['views_unique'],
            'clones_total': data['clones_total'],
            'clones_unique': data['clones_unique']
        })
    
    print(f"✅ Saved: {json_file}")
    print(f"✅ Updated: {csv_file}")

if __name__ == "__main__":
    print("📊 Collecting metrics for", REPO)
    data = get_traffic()
    save_metrics(data)
    print(f"\n📈 Today's stats:")
    print(f"  Views: {data['views_total']} ({data['views_unique']} unique)")
    print(f"  Clones: {data['clones_total']} ({data['clones_unique']} unique)")
