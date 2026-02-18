from fastapi import FastAPI, Query
import json, random, hashlib, datetime
from typing import Optional

app = FastAPI(title="CommercePulse Mock API")

# --- Helper functions from your original script ---
def stable_id(*parts):
    s = "|".join(map(str, parts))
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]

def iso(dt):
    return dt.replace(microsecond=0).isoformat() + "Z"

def rand_dt(day_start, day_end):
    delta = int((day_end-day_start).total_seconds())
    return day_start + datetime.timedelta(seconds=random.randint(0, max(delta,1)))

# ... (Keep your original vendor_payload function here) ...

@app.get("/events")
def get_events(
    events: int = 100,
    date: Optional[str] = None,
    dup_rate: float = 0.05,
    late_rate: float = 0.10,
    schema_drift_rate: float = 0.15,
    seed: Optional[int] = None
):
    if seed:
        random.seed(seed)
    
    day = datetime.date.fromisoformat(date) if date else datetime.date.today()
    day_start = datetime.datetime.combine(day, datetime.time(0,0,0))
    day_end = datetime.datetime.combine(day, datetime.time(23,59,59))

    # In-memory order pool (since Render Free tier has no persistent disk)
    order_pool = [f"ORD-{day.strftime('%y%m%d')}-{i:05d}" for i in range(1, 500)]
    event_types = ["order_created","payment_succeeded","refund_issued","shipment_updated","order_updated"]

    generated = []
    for _ in range(events):
        vendor = random.choice(["vendor_a","vendor_b","vendor_c"])
        et = random.choices(event_types, weights=[0.20, 0.33, 0.12, 0.25, 0.10])[0]
        order_id = random.choice(order_pool)
        
        ingested_at = rand_dt(day_start, day_end)
        
        if random.random() < late_rate:
            event_time = ingested_at - datetime.timedelta(days=random.randint(1, 7))
        else:
            event_time = ingested_at - datetime.timedelta(minutes=random.randint(0, 120))

        payload = vendor_payload(et, vendor, order_id, event_time, 10000, 
                                 schema_drift=(random.random() < schema_drift_rate))

        doc = {
            "event_id": stable_id(vendor, et, order_id, iso(event_time), str(random.random())),
            "event_type": et,
            "event_time": iso(event_time),
            "vendor": vendor,
            "payload": payload,
            "ingested_at": iso(ingested_at)
        }
        generated.append(doc)
        if random.random() < dup_rate:
            generated.append(doc.copy())

    return {"count": len(generated), "events": generated}