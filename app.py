from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import shlex
import time
import requests
import socket

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)


def run_command(cmd: str):
    """Run a shell command and return its output as text."""
    print(f"[+] Running: {cmd}")
    completed = subprocess.run(
        shlex.split(cmd),
        text=True,
        capture_output=True
    )
    output = completed.stdout + completed.stderr
    return output, completed.returncode


@app.get("/api/ping")
def ping():
    """Simple health check."""
    return jsonify({"status": "ok"})


# ---------- Nmap scan ----------

@app.post("/api/test-nmap")
def test_nmap():
    """
    JSON body: { "target": "20.34.1.10" }
    Runs: nmap -sV <target>
    """
    data = request.get_json(silent=True) or {}
    target = data.get("target", "").strip()

    if not target:
        return jsonify({"error": "target is required"}), 400

    cmd = f"nmap -sV {target}"
    output, code = run_command(cmd)

    return jsonify({
        "target": target,
        "exit_code": code,
        "output": output
    })


# ---------- HTTP load test ----------

@app.post("/api/http-load-test")
def http_load_test():
    """
    JSON body: {
      "url": "http://192.168.56.104:8000/",
      "requests": 50,
      "timeout": 5.0
    }

    Sends many HTTP GET requests to a URL you control and returns statistics.
    """
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    total_requests = int(data.get("requests", 50))
    timeout = float(data.get("timeout", 5.0))

    if not url:
        return jsonify({"error": "url is required"}), 400
    if total_requests < 1:
        return jsonify({"error": "requests must be >= 1"}), 400

    success = 0
    failures = 0
    latencies = []

    for _ in range(total_requests):
        start = time.time()
        try:
            resp = requests.get(url, timeout=timeout)
            elapsed_ms = (time.time() - start) * 1000.0
            latencies.append(elapsed_ms)
            if 200 <= resp.status_code < 400:
                success += 1
            else:
                failures += 1
        except Exception as e:
            print(f"[!] HTTP request failed: {e}")
            failures += 1

    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
    else:
        avg_latency = min_latency = max_latency = None

    return jsonify({
        "url": url,
        "total_requests": total_requests,
        "success": success,
        "failures": failures,
        "avg_latency_ms": avg_latency,
        "min_latency_ms": min_latency,
        "max_latency_ms": max_latency,
    })


# ---------- HTTP capacity test ----------

@app.post("/api/capacity-test")
def capacity_test():
    """
    JSON body:
    {
      "url": "http://192.168.56.104:8000/",
      "steps": [10, 25, 50, 100],
      "timeout": 5.0
    }

    For each step N, runs the HTTP load test with N requests and
    evaluates whether the service is still 'healthy'.
    """
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    steps = data.get("steps", [10, 25, 50, 100])
    timeout = float(data.get("timeout", 5.0))

    if not url:
        return jsonify({"error": "url is required"}), 400

    clean_steps = []
    for s in steps:
        try:
            n = int(s)
            if n > 0:
                clean_steps.append(n)
        except Exception:
            continue

    if not clean_steps:
        return jsonify({"error": "steps must contain positive integers"}), 400

    MIN_SUCCESS_RATE = 0.95   # 95%
    MAX_AVG_LAT_MS = 300.0
    MAX_MAX_LAT_MS = 1000.0

    results = []
    max_healthy = 0

    for n in clean_steps:
        print(f"[+] Capacity test: {n} requests to {url}")
        success = 0
        failures = 0
        latencies = []

        for _ in range(n):
            start = time.time()
            try:
                resp = requests.get(url, timeout=timeout)
                elapsed_ms = (time.time() - start) * 1000.0
                latencies.append(elapsed_ms)
                if 200 <= resp.status_code < 400:
                    success += 1
                else:
                    failures += 1
            except Exception as e:
                print(f"[!] HTTP request failed: {e}")
                failures += 1

        total = success + failures
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
        else:
            avg_latency = min_latency = max_latency = None

        success_rate = (success / total) if total > 0 else 0.0

        healthy = (
            success_rate >= MIN_SUCCESS_RATE
            and avg_latency is not None
            and max_latency is not None
            and avg_latency <= MAX_AVG_LAT_MS
            and max_latency <= MAX_MAX_LAT_MS
        )

        if healthy:
            max_healthy = n

        results.append({
            "requests": n,
            "success": success,
            "failures": failures,
            "success_rate": success_rate,
            "avg_latency_ms": avg_latency,
            "min_latency_ms": min_latency,
            "max_latency_ms": max_latency,
            "healthy": healthy
        })

        if not healthy:
            break

    summary = {
        "url": url,
        "steps": clean_steps,
        "results": results,
        "max_healthy_requests": max_healthy,
        "thresholds": {
            "min_success_rate": MIN_SUCCESS_RATE,
            "max_avg_latency_ms": MAX_AVG_LAT_MS,
            "max_max_latency_ms": MAX_MAX_LAT_MS
        }
    }

    return jsonify(summary)


# ---------- Ping statistics ----------

@app.post("/api/ping-stats")
def ping_stats():
    """
    JSON body: { "target": "192.168.56.1", "count": 4 }
    Runs: ping -c <count> <target>
    Returns packet loss and avg/min/max RTT if available.
    """
    data = request.get_json(silent=True) or {}
    target = data.get("target", "").strip()
    count = int(data.get("count", 4))

    if not target:
        return jsonify({"error": "target is required"}), 400
    if count < 1:
        return jsonify({"error": "count must be >= 1"}), 400

    cmd = f"ping -c {count} {target}"
    output, code = run_command(cmd)

    packet_loss = None
    avg_rtt = min_rtt = max_rtt = None

    for line in output.splitlines():
        if "packet loss" in line:
            try:
                packet_loss = line.split("%")[0].split()[-1] + "%"
            except Exception:
                pass

    for line in output.splitlines():
        if "min/avg/max" in line:
            try:
                stats_part = line.split("=")[1].strip().split(" ")[0]
                mins, avgs, maxs, *_ = stats_part.split("/")
                min_rtt = float(mins)
                avg_rtt = float(avgs)
                max_rtt = float(maxs)
            except Exception:
                pass

    return jsonify({
        "target": target,
        "exit_code": code,
        "output": output,
        "packet_loss": packet_loss,
        "min_rtt_ms": min_rtt,
        "avg_rtt_ms": avg_rtt,
        "max_rtt_ms": max_rtt,
    })


# ---------- Traceroute ----------

@app.post("/api/traceroute")
def traceroute():
    """
    JSON body: { "target": "example.com", "max_hops": 20 }
    Runs: traceroute -m <max_hops> <target>
    """
    data = request.get_json(silent=True) or {}
    target = data.get("target", "").strip()
    max_hops = int(data.get("max_hops", 20))

    if not target:
        return jsonify({"error": "target is required"}), 400

    cmd = f"traceroute -m {max_hops} {target}"
    output, code = run_command(cmd)

    return jsonify({
        "target": target,
        "exit_code": code,
        "output": output
    })


# ---------- DNS lookup ----------

@app.post("/api/dns-lookup")
def dns_lookup():
    """
    JSON body: { "hostname": "example.com" }
    Uses Python's socket.getaddrinfo to resolve A/AAAA records.
    """
    data = request.get_json(silent=True) or {}
    hostname = data.get("hostname", "").strip()

    if not hostname:
        return jsonify({"error": "hostname is required"}), 400

    addrs = set()
    try:
        info = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in info:
            ip = sockaddr[0]
            addrs.add(ip)
        return jsonify({
            "hostname": hostname,
            "addresses": sorted(addrs),
        })
    except Exception as e:
        return jsonify({
            "hostname": hostname,
            "error": str(e),
            "addresses": []
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
