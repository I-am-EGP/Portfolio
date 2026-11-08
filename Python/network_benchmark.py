#Simple network benchmark script, make sure speedtest-cli module is installed in order to work properly

import csv
from datetime import datetime
from pathlib import Path

import speedtest


def run_benchmark():
    s = speedtest.Speedtest()
    s.get_servers()
    s.get_best_server()
    s.download()
    s.upload()
    return s.results.dict()


def main():
    print("Running test... (can take up to 30s)")
    r = run_benchmark()

    download_mbps = r["download"] / 1_000_000
    upload_mbps = r["upload"] / 1_000_000
    ping_ms = r["ping"]
    server = f'{r["server"]["sponsor"]} ({r["server"]["name"]})'

    print(f"Server:    {server}")
    print(f"Download:  {download_mbps:.2f} Mbps")
    print(f"Upload:    {upload_mbps:.2f} Mbps")
    print(f"Ping:      {ping_ms:.1f} ms")

    # Store history in a CSV file
    history_file = Path.home() / "history_benchmark.csv"
    new = not history_file.exists()
    with history_file.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date_hour", "server", "download_mbps", "upload_mbps", "ping_ms"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), server,
                    f"{download_mbps:.2f}", f"{upload_mbps:.2f}", f"{ping_ms:.1f}"])


if __name__ == "__main__":
     main()
