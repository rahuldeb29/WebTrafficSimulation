<img width="1919" height="919" alt="image" src="https://github.com/user-attachments/assets/2b6c8f54-47d4-4f6e-8d74-b84418faf3b3" />
Web Traffic Simulations

A simple but powerful tool for load-testing APIs, analyzing server performance, and running network diagnostics.

This project consists of:

A frontend dashboard (index.html) for running tests and visualizing results

A Flask backend (app.py) that performs the actual network operations

Real-time charts, metrics, and a live console output

It lets you run HTTP load tests, capacity tests, Nmap scans, ping tests, DNS lookups, and traceroutes — all from a clean UI.

 How It Works (Simple Explanation)
1️ You click a button on the UI

Example: “Run HTTP Load Test”.

2️ The frontend sends a request to the Flask backend (app.py)

The UI calls endpoints like:

POST /api/http-load-test
POST /api/capacity-test
POST /api/test-nmap
POST /api/ping-stats
POST /api/traceroute
POST /api/dns-lookup

3️ The backend performs the operation

Examples:

Sends 200 HTTP GET requests to your API

Runs nmap -sV <target>

Runs the Linux ping command

Runs traceroute

Resolves DNS records

4️ The backend returns results to the frontend

It returns things like:

Success count

Failures

Latency (avg, min, max)

Success rate

Nmap output

Ping loss & RTTs

Traceroute hops

DNS records

5️ The frontend updates everything in real time

The success/failure chart updates

Performance metrics update

Load capacity bar updates

Console prints logs line-by-line

A verdict + recommendation appear

Everything feels live and interactive.

 Main Features
 HTTP Load Test

Sends N requests to a given URL, then returns:

Success / failures

Avg latency

Max latency

Performance summary

 Capacity Test

Runs multiple steps like:

10, 25, 50, 100


For each step the backend:

Sends that many requests

Checks if the success rate & latency are healthy

Stops if the server becomes slow or unstable

Calculates the maximum healthy capacity

The UI then estimates your server’s performance limit.

 Nmap Scan

Runs:

nmap -sV <target>


and shows full scan output inside the console.

 Project Files
index.html          → Main dashboard UI  
scan-history.html   → View past test results  
api.js              → Frontend API connector  
app.py              → Flask backend (handles all testing logic)  
README.md           → Documentation  

🛠️ How to Run the Project
1. Install backend dependencies

Inside your project folder:

pip install flask flask-cors requests

2. Start the backend server

Run:

python app.py


Flask starts on:

http://localhost:5000

3. Open the frontend

Just open index.html in your browser.

Everything will work automatically — the UI connects to the backend over HTTP.

 Example Usage (From Screenshot)

For 215 requests:

Success: 215

Failures: 0

Avg Latency: 9.6ms

Max Latency: 23ms

Estimated Capacity: ~323 requests

Verdict: Healthy

Recommendation: Increase load to test further
