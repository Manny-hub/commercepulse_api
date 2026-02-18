from fastapi import FastAPI, Query
import json, random, hashlib, datetime
from typing import Optional

VENDORS = ["vendor_a","vendor_b","vendor_c"]
REGIONS = ["Lagos","Abuja","Kano","Kaduna","PH"]
CURRENCIES = ["NGN","USD"]
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
def vendor_payload(event_type, vendor, order_id, dt, base_amount, schema_drift=False):
    currency = random.choices(CURRENCIES, weights=[0.88, 0.12])[0]
    if currency == "USD":
        fx = 950 + random.randint(-80, 120)
        amount = round(base_amount / fx, 2)
    else:
        amount = base_amount

    if vendor == "vendor_a":
        if event_type == "order_created":
            payload = {
                "orderRef": order_id,
                "created": dt.strftime("%Y-%m-%d %H:%M"),
                "customer": {"email": f"user{random.randint(1,2500)}@example.com"},
                "total": amount,
                "currency": currency,
                "region": random.choice(REGIONS),
                "items": [{"sku": f"SKU-{random.randint(0,219):04d}", "qty": random.randint(1,3), "price": random.choice([2500,4000,6500,9000,12000])}
                          for _ in range(random.randint(1,4))]
            }
            if schema_drift:
                payload["totalAmount"] = payload.pop("total")
                payload["buyer"] = payload.pop("customer")
        elif event_type == "payment_succeeded":
            payload = {"orderRef": order_id, "paidAt": dt.strftime("%Y/%m/%d %H:%M:%S"), "status": "SUCCESS",
                       "amount": amount, "currency": currency, "method": random.choice(["card","bank_transfer","ussd"]),
                       "txRef": f"TX-{stable_id(order_id, dt, amount)}"}
            if schema_drift:
                payload["payment_status"] = payload.pop("status")
        elif event_type == "refund_issued":
            partial = random.random() < 0.55
            items = [{"sku": f"SKU-{random.randint(0,219):04d}", "qty": 1, "amount": random.choice([1500,2500,4000,6500])}
                     for _ in range(random.randint(1,2))] if partial else None
            payload = {"orderRef": order_id, "refundedAt": dt.strftime("%Y-%m-%dT%H:%M:%S"),
                       "amount": amount if not partial else sum(x["amount"] for x in items),
                       "currency": currency, "reason": random.choice(["customer_request","duplicate","damaged","late_delivery"]),
                       "items": items}
            if schema_drift:
                payload["refunded_items"] = payload.pop("items")
        elif event_type == "shipment_updated":
            payload = {"orderRef": order_id, "tracking": f"TRK-{stable_id(order_id, vendor)}",
                       "status": random.choice(["CREATED","PICKED_UP","IN_TRANSIT","DELIVERED"]),
                       "updateTime": iso(dt)}
            if schema_drift:
                payload["update_time"] = payload.pop("updateTime")
        else:
            payload = {"orderRef": order_id, "updatedAt": iso(dt),
                       "change": random.choice(["address_change","qty_change","phone_change"]),
                       "notes": "customer requested update"}
            if schema_drift:
                payload["updated_at"] = payload.pop("updatedAt")

    elif vendor == "vendor_b":
        if event_type == "order_created":
            payload = {"order_id": order_id, "created_at": iso(dt),
                       "buyerEmail": f"user{random.randint(1,2500)}@mail.com",
                       "totalAmount": amount, "currencyCode": currency,
                       "state": random.choice(REGIONS),
                       "line_items": [{"sku": f"SKU-{random.randint(0,219):04d}", "quantity": random.randint(1,3), "unit_price": random.choice([2500,4000,6500,9000,12000])}
                                      for _ in range(random.randint(1,4))]}
            if schema_drift:
                payload["currency"] = payload.pop("currencyCode")
        elif event_type == "payment_succeeded":
            payload = {"order_id": order_id, "paid_at": iso(dt), "payment_status": "SUCCESS",
                       "amountPaid": amount, "currencyCode": currency,
                       "channel": random.choice(["card","bank_transfer","ussd"]),
                       "transaction_id": stable_id(order_id, dt, amount)}
            if schema_drift:
                payload["amount_paid"] = payload.pop("amountPaid")
        elif event_type == "refund_issued":
            partial = random.random() < 0.55
            refunded_items = [{"sku": f"SKU-{random.randint(0,219):04d}", "qty": 1, "amount": random.choice([1500,2500,4000,6500])}
                              for _ in range(random.randint(1,2))] if partial else None
            payload = {"order_id": order_id, "refunded_at": iso(dt), "refundAmount": amount if not partial else sum(x["amount"] for x in refunded_items),
                       "currencyCode": currency, "refund_reason": random.choice(["customer_request","duplicate","damaged","late_delivery"]),
                       "refunded_items": refunded_items}
            if schema_drift:
                payload["reason"] = payload.pop("refund_reason")
        elif event_type == "shipment_updated":
            payload = {"order_id": order_id, "tracking_code": f"TRK{random.randint(1000000,9999999)}",
                       "shipment_status": random.choice(["CREATED","PICKED_UP","IN_TRANSIT","DELIVERED"]),
                       "time": iso(dt)}
            if schema_drift:
                payload["status"] = payload.pop("shipment_status")
        else:
            payload = {"order_id": order_id, "updated_at": iso(dt), "change_type": random.choice(["address_change","qty_change","phone_change"])}
            if schema_drift:
                payload["change"] = payload.pop("change_type")

    else:
        if event_type == "order_created":
            payload = {"order": {"id": order_id, "ts": int(dt.timestamp())},
                       "email": f"user{random.randint(1,2500)}@pulse.africa",
                       "amount": amount, "ccy": currency,
                       "geo": {"region": random.choice(REGIONS)},
                       "items": [{"productSku": f"SKU-{random.randint(0,219):04d}", "qty": random.randint(1,3), "price": random.choice([2500,4000,6500,9000,12000])}
                                 for _ in range(random.randint(1,4))]}
            if schema_drift:
                payload["items"] = [{"sku": it["productSku"], "qty": it["qty"], "price": it["price"]} for it in payload["items"]]
        elif event_type == "payment_succeeded":
            payload = {"order": order_id, "timestamp": int(dt.timestamp()), "state": "SUCCESS",
                       "amt": amount, "ccy": currency, "paymentMethod": random.choice(["card","bank_transfer","ussd"]),
                       "txn": f"TRX{random.randint(100000,999999)}"}
            if schema_drift:
                payload["payment_state"] = payload.pop("state")
        elif event_type == "refund_issued":
            partial = random.random() < 0.55
            items = [{"sku": f"SKU-{random.randint(0,219):04d}", "qty": 1, "amount": random.choice([1500,2500,4000,6500])}
                     for _ in range(random.randint(1,2))] if partial else None
            payload = {"order": order_id, "ts": int(dt.timestamp()), "amt": amount if not partial else sum(x["amount"] for x in items),
                       "ccy": currency, "reason": random.choice(["customer_request","duplicate","damaged","late_delivery"]),
                       "items_refunded": items}
            if schema_drift:
                payload["items"] = payload.pop("items_refunded")
        elif event_type == "shipment_updated":
            payload = {"order": {"id": order_id}, "tracking": f"{random.randint(100000000,999999999)}",
                       "state": random.choice(["CREATED","PICKED_UP","IN_TRANSIT","DELIVERED"]),
                       "ts": int(dt.timestamp())}
            if schema_drift:
                payload["status"] = payload.pop("state")
        else:
            payload = {"order": order_id, "ts": int(dt.timestamp()), "change": random.choice(["address_change","qty_change","phone_change"]),
                       "notes": "legacy update"}
            if schema_drift:
                payload["note"] = payload.pop("notes")
    return payload

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