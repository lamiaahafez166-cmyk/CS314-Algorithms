"""Write a short description of the machine used for the measurements."""

import os
import platform
import subprocess
import sys


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return ""


def describe() -> str:
    lines = [f"Python:   {sys.version.split()[0]} ({platform.python_implementation()})",
             f"Platform: {platform.platform()}",
             f"Machine:  {platform.machine()}"]
    lscpu = _run(["lscpu"])
    for line in lscpu.splitlines():
        key = line.split(":")[0].strip()
        if key in ("Model name", "CPU(s)", "L1d cache", "L2 cache", "L3 cache"):
            lines.append(line.strip())
    gpp = _run(["g++", "--version"]).splitlines()
    if gpp:
        lines.append(f"g++:      {gpp[0]}")
    return "\n".join(lines) + "\n"


def write(out_dir: str) -> None:
    with open(os.path.join(out_dir, "environment.txt"), "w") as f:
        f.write(describe())


if __name__ == "__main__":
    print(describe())
