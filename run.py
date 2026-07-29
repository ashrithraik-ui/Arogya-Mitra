import subprocess
import os
import sys
import time
import socket


def get_local_ip_addresses():
    """Detect all local IP addresses of this machine."""
    ips = []
    try:
        # Method 1: Connect to an external address to find the primary LAN IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
        if primary_ip and primary_ip not in ips:
            ips.append(primary_ip)
    except Exception:
        pass

    try:
        # Method 2: Get all IPs from hostname
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except Exception:
        pass

    return ips


def print_server_banner(ips, port=8000):
    """Print a clear banner showing all connection URLs."""
    border = "═" * 60
    print(f"\n╔{border}╗")
    print(f"║{'ArogyaMitra AI — Server Started':^60}║")
    print(f"╠{border}╣")
    print(f"║{'':^60}║")
    print(f"║  {'📡 Backend running on port ' + str(port):<58}║")
    print(f"║{'':^60}║")
    print(f"║  {'🖥️  Local (this PC):':40}║")
    print(f"║    {'http://localhost:' + str(port):<56}║")
    print(f"║{'':^60}║")

    if ips:
        print(f"║  {'📱 For Android App / Mobile (same Wi-Fi):':40}║")
        for ip in ips:
            url = f"http://{ip}:{port}"
            print(f"║    {'➜  ' + url:<56}║")
        print(f"║{'':^60}║")
        print(f"║  {'👆 Enter one of the above URLs in the app Settings':40}║")
    else:
        print(f"║  {'⚠️  Could not detect LAN IP. Use ipconfig to find it.':<58}║")

    print(f"║{'':^60}║")
    print(f"║  {'📞 Web Voice Call (Any Device):':40}║")
    print(f"║    {'http://localhost:' + str(port) + '/call':<56}║")
    if ips:
        print(f"║    {'http://' + ips[0] + ':' + str(port) + '/call':<56}║")
    print(f"║{'':^60}║")
    print(f"║  {'🇮🇳 Exotel Telephony AI (+91 ExoPhone):':40}║")
    print(f"║    {'POST http://localhost:' + str(port) + '/exotel/incoming':<56}║")
    print(f"║  {'📖 Exotel Setup: http://localhost:' + str(port) + '/exotel/setup':<58}║")
    print(f"║{'':^60}║")
    print(f"║  {'📞 Twilio Voice AI Webhook:':40}║")
    print(f"║    {'POST http://localhost:' + str(port) + '/voice/incoming':<56}║")
    print(f"║  {'📖 Setup Guide: http://localhost:' + str(port) + '/voice/setup':<58}║")
    print(f"║{'':^60}║")
    print(f"║  {'📄 API Docs:  http://localhost:' + str(port) + '/docs':<58}║")
    print(f"║{'':^60}║")
    print(f"╚{border}╝\n")


def run():
    print("Starting ArogyaMitra AI - Frontend & Backend concurrently...")

    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "arogya-mitra")

    # Load .env from backend directory into environment
    env_file = os.path.join(backend_dir, ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key.strip(), value.strip())
        print(f"[OK] Loaded environment from {env_file}")

    # Detect IP addresses
    ips = get_local_ip_addresses()

    # Start Backend
    print("[1/2] Starting backend on 0.0.0.0:8000 ...")
    backend_env = os.environ.copy()
    backend_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
    if not os.path.exists(backend_python):
        # Fall back to system Python
        backend_python = sys.executable
        print(f"[!] venv not found, using system Python: {backend_python}")

    backend_process = subprocess.Popen(
        [backend_python, "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=root_dir,
        env=backend_env
    )

    # Give backend a moment to start
    time.sleep(2)

    # Print the connection banner
    print_server_banner(ips, port=8000)

    # Start Frontend
    print("[2/2] Starting frontend dev server...")
    frontend_env = os.environ.copy()
    frontend_env["VITE_API_URL"] = "http://localhost:8000"
    
    # Check if npm exists (we can use shell=True to rely on PATH)
    frontend_process = subprocess.Popen(
        "npm run dev",
        cwd=frontend_dir,
        env=frontend_env,
        shell=True
    )

    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down both processes...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    run()
