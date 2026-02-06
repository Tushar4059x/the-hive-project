import random
import time
import json
import uuid
from datetime import datetime

LOG_TYPES = ["OPTIMIZATION", "SECURITY_SCAN", "DATA_INGESTION", "NEURAL_SYNC", "PROTOCOL_HANDSHAKE"]
STATUSES = ["SUCCESS", "WARNING", "CRITICAL", "PENDING"]

def generate_log_event():
    log_type = random.choice(LOG_TYPES)
    status = random.choice(STATUSES)
    
    event = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "type": log_type,
        "status": status,
        "metrics": {
            "latency_ms": random.randint(1, 200),
            "cpu_usage": f"{random.randint(10, 99)}%",
            "memory_usage": f"{random.randint(200, 4096)}MB"
        },
        "payload_hash": f"0x{random.getrandbits(128):032x}"
    }
    
    # Add some random "teching" fields based on type
    if log_type == "OPTIMIZATION":
        event["details"] = {"iterations": random.randint(1000, 100000), "improvement": f"{random.random()*10:.2f}%"}
    elif log_type == "SECURITY_SCAN":
        event["details"] = {"target": f"192.168.1.{random.randint(1, 255)}", "vulnerabilities_found": random.randint(0, 5)}
        
    return event

async def event_generator():
    """Yields a stream of log events"""
    while True:
        data = generate_log_event()
        yield json.dumps(data) + "\n"
        # Simulate high-speed data stream, variable speed
        await asyncio.sleep(random.uniform(0.05, 0.3))

import asyncio
