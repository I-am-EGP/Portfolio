# Simple health checker script
# Make sure psutil module is installed

import os
import platform
import socket
import time
from datetime import timedelta

import psutil


CPU_THRESHOLD = 80.0       # percent
MEMORY_THRESHOLD = 80.0    # percent
DISK_THRESHOLD = 85.0      # percent


# CPU CHECK
def check_cpu():
    usage = psutil.cpu_percent(interval=1)
    status = "OK" if usage < CPU_THRESHOLD else "WARNING"
    return status, f"CPU usage: {usage}% (threshold: {CPU_THRESHOLD}%)"


# MEMORY CHECK
def bytes_to_gb(value):
    return round(value / (1024 ** 3), 2)


def check_memory():
    memory = psutil.virtual_memory()
    status = "OK" if memory.percent < MEMORY_THRESHOLD else "WARNING"
    message = (
        f"Memory usage: {memory.percent}% "
        f"({bytes_to_gb(memory.used)} GB used / "
        f"{bytes_to_gb(memory.total)} GB total)"
    )
    return status, message


# DISK CHECK
def check_disk():
    path = os.path.abspath(os.sep)  # root drive on most systems
    disk = psutil.disk_usage(path)
    status = "OK" if disk.percent < DISK_THRESHOLD else "WARNING"
    message = (
        f"Disk usage ({path}): {disk.percent}% "
        f"({bytes_to_gb(disk.used)} GB used / "
        f"{bytes_to_gb(disk.total)} GB total)"
    )
    return status, message


# UPTIME CHECK
def check_uptime():
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime = timedelta(seconds=int(uptime_seconds))
    return "OK", f"System uptime: {uptime}"


# BASIC SYSTEM INFORMATION
def system_info():
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "release": platform.release(),
        "python_version": platform.python_version(),
    }


# MAIN FUNCTION
def main():
    print("=" * 60)
    print("SYSTEM HEALTH CHECK")
    print("=" * 60)

    info = system_info()
    print(f"Hostname        : {info['hostname']}")
    print(f"Platform        : {info['platform']} {info['release']}")
    print(f"Python version  : {info['python_version']}")
    print("-" * 60)

    checks = [
        check_cpu(),
        check_memory(),
        check_disk(),
        check_uptime(),
    ]

    overall_status = "OK"

    for status, message in checks:
        print(f"[{status}] {message}")
        if status != "OK":
            overall_status = "WARNING"

    print("-" * 60)
    print(f"Overall status  : {overall_status}")
    print("=" * 60)

    return overall_status


if __name__ == "__main__":
    main()
