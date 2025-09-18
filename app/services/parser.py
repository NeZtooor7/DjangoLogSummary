import re, hashlib
from collections import defaultdict

TS = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[,\.]\d{3})?(?:Z)?)\s+(?P<rest>.*)$'
)
LEVEL = re.compile(r'\b(INFO|WARN|WARNING|ERROR|DEBUG|CRITICAL)\b', re.I)

def parse_log_lines(lines, max_events=5000):
    events = []
    current = None

    for raw in lines:
        line = raw.rstrip("\n")
        matches = TS.match(line)
        if matches:
            # guardar el anterior
            if current:
                events.append(current)
            rest = matches.group("rest")
            level = LEVEL.search(rest)
            current = {
                "ts": matches.group("timestamp"),
                "level": (level.group(0).upper() if level else "INFO"),
                "message": rest,
                "stack": []
            }
        else:
            if current is not None and current["stack"] is not None:
                current["stack"].append(line)
            # si no hay current, línea huérfana: ignórala o acumula en "stack_orphan"
        if len(events) >= max_events:
            break

    if current:
        events.append(current)

    # fingerprint y counts
    buckets = defaultdict(lambda: {"count":0, "example":None})
    for e in events:
        base = e["message"].split(" - ")[0][:200]
        first_stack = e["stack"][0] if e["stack"] else ""
        fp_src = f'{e["level"]}|{base}|{first_stack[:200]}'
        fp = hashlib.sha1(fp_src.encode()).hexdigest()[:8]
        buckets[fp]["count"] += 1
        if not buckets[fp]["example"]:
            buckets[fp]["example"] = e

    # top-5 for frequency + muestras
    top = sorted(
        [{"fingerprint": k, "count": v["count"], "example": v["example"]} for k,v in buckets.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]

    return {
        "total_events": len(events),
        "top_errors": top,
    }
