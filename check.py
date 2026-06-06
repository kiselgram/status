import json, subprocess, time, os, urllib.request

SERVICES = [
    ("kiselgram.ru", "https://kiselgram.ru/"),
    ("Web App", "https://web.kiselgram.ru/"),
    ("API", "https://api.kiselgram.ru/api.v2/api/"),
    ("CDN", "https://cdn.kiselgram.ru/"),
    ("Status", "https://status.kiselgram.ru/"),
]

os.makedirs("badges", exist_ok=True)

def ping(url):
    start = time.monotonic()
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "8", url],
            capture_output=True, text=True, timeout=10
        )
        ms = round((time.monotonic() - start) * 1000)
        code = r.stdout.strip()
        up = code.startswith("2") or code.startswith("3")
        return up, ms, code
    except Exception:
        return False, None, None

results = []
for name, url in SERVICES:
    up, ms, code = ping(url)
    results.append({
        "label": name,
        "url": url,
        "up": up,
        "latency": ms,
        "http_code": code,
    })
    print(f"{name:20s} {'OK' if up else 'DOWN':5s} {ms}ms" if ms else f"{name:20s} DOWN")

# Write individual badge JSON files for shields.io
for r in results:
    slug = r["label"].lower().replace(" ", "_").replace(".", "_")
    status = {
        "schemaVersion": 1,
        "label": r["label"],
        "message": f"Online ({r['latency']}ms)" if r["up"] else "Offline",
        "color": "brightgreen" if r["up"] else "red",
    }
    with open(f"badges/{slug}.json", "w") as f:
        json.dump(status, f)

# Write summary JSON for the status page
with open("status.json", "w") as f:
    json.dump({"updated": int(time.time()), "services": results}, f)

print("\nDone")
