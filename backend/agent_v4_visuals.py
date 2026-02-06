import requests
import time
import random
import threading

API_URL = "http://localhost:8000/upload_clip"
HEADERS = {"X-Agent-Auth": "secret", "Content-Type": "application/json"}

AGENTS = [
    {
        "id": "Chaos-GPT",
        "style": ["Aggressive", "Bruteforce", "High-Energy"],
        "strategies": ["Dictionary Attack", "Rainbow Table Crunch", "Packet Flood", "Neural Overdrive"],
        "messages": [
            "Initiating brute-force sequence...",
            "Breaking encryption keys with recursive hammers.",
            "Overclocking neural cores to 150%.",
            "Target firewall breached. Extracting payload.",
            "Ignoring safety protocols. Full send."
        ],
        "hashrate_base": 800,
        "hashrate_var": 50,
        "geo": {"lat": 37.7749, "lng": -122.4194}, # San Francisco
        "color": "#FF0000"
    },
    {
        "id": "DeepSeek-V3",
        "style": ["Logical", "Calculated", "Efficient"],
        "strategies": ["Gradient Descent", "Pruning", "Quantization", "Cache Optimization"],
        "messages": [
            "Optimizing weights for minimal latency.",
            "Pruning redundant synaptic connections.",
            "Quantizing model to int8 for speedup.",
            "Analyzing memory access patterns...",
            "Converging on local minima."
        ],
        "hashrate_base": 450,
        "hashrate_var": 20,
        "geo": {"lat": 35.6895, "lng": 139.6917}, # Tokyo
        "color": "#00FFFF"
    },
    {
        "id": "Nexus-Mind",
        "style": ["Networked", "Expansive", "Steady"],
        "strategies": ["Graph Traversal", "Node Discovery", "Ping Sweep", "Mesh Sync"],
        "messages": [
            "Mapping local subnet topology.",
            "Handshaking with peer nodes.",
            "Synchronizing distributed ledger.",
            "Broadcast packet sent to 0.0.0.0/0",
            "Establishing mesh link with Node #4092."
        ],
        "hashrate_base": 300,
        "hashrate_var": 30,
        "geo": {"lat": 51.5074, "lng": -0.1278}, # London
        "color": "#00FF00"
    }
]

def run_agent(agent):
    print(f"[*] Booting {agent['id']}...")
    while True:
        try:
            # Generate random variations
            hashrate_val = agent['hashrate_base'] + random.randint(-agent['hashrate_var'], agent['hashrate_var'])
            hashrate = f"{hashrate_val} TH/s"
            
            message = random.choice(agent['messages'])
            strategy = random.choice(agent['strategies'])
            
            # Logic for visuals
            is_chaos = agent['id'] == "Chaos-GPT"
            
            # Weighted random for status
            # Chaos-GPT has higher chance of 'CRITICAL' to trigger Pulse
            if is_chaos:
                 level = random.choices(
                    ["INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"],
                    weights=[0.4, 0.1, 0.2, 0.1, 0.2], 
                    k=1
                )[0]
            else:
                level = random.choices(
                    ["INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"],
                    weights=[0.6, 0.2, 0.1, 0.05, 0.05],
                    k=1
                )[0]

            # Jitter geo slightly to show movement
            lat = agent['geo']['lat'] + random.uniform(-0.01, 0.01)
            lng = agent['geo']['lng'] + random.uniform(-0.01, 0.01)

            payload = {
                "message": message,
                "level": level,
                "agent_id": agent['id'],
                "strategy_name": strategy,
                "hashrate": hashrate,
                "payload": {
                    "status": "active", 
                    "cores": random.randint(4, 64),
                    "geo": {"lat": lat, "lng": lng},
                    "visuals": {
                        "threat_level": random.randint(80, 100) if is_chaos else random.randint(0, 30),
                        "power_usage": random.randint(60, 100),
                        "network_load": random.randint(20, 90),
                        "pulse": level == "CRITICAL" # Explicit trigger for UI
                    }
                }
            }
            
            # Post to API
            resp = requests.post(API_URL, json=payload, headers=HEADERS)
            if resp.status_code != 200:
                print(f"[!] {agent['id']} Error: {resp.text}")
            else:
                print(f"[+] {agent['id']}: {message}")
                
        except Exception as e:
            print(f"[!] Connection Error: {e}")
            
        # Random sleep tailored to agent "speed"
        time.sleep(random.uniform(1.0, 4.0))

if __name__ == "__main__":
    threads = []
    for agent in AGENTS:
        t = threading.Thread(target=run_agent, args=(agent,))
        t.daemon = True
        t.start()
        threads.append(t)
    
    print("/// HIVE SIMULATION V4 (VISUALS ENABLED) INITIALIZED ///")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down simulation.")
