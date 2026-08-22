#!/usr/bin/env python3
"""
xrd-save.py — Save running-config from all XRd nodes in a Containerlab lab.

Fast + parallel version. Saves all nodes at the same time using threads, so
total time is roughly one node (~3-4s) instead of 7x that.

The sbezverk/xrd-control-plane image needs a real pty + interactive login for
xr_cli.sh. We delete any stale harddisk file before writing so a failed write
can never result in copying old config.

Usage:
  python3 xrd-save.py
  python3 xrd-save.py --prefix clab-segment-routing-lab2 --outdir config
"""

import argparse
import os
import pty
import select
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

XR_USER = "clab"
XR_PASS = "clab@123"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, r.stdout.strip(), r.stderr.strip()


def write_via_pty(container, xr_cmd, timeout=12, idle_gap=0.6):
    """Log in via a real pty and run the write command. Answers login prompts
    and the file-overwrite [confirm] prompt."""
    sends = [
        (None, ""),
        ("Username:", XR_USER),
        ("Password:", XR_PASS),
        ("#", xr_cmd),
        ("confirm", ""),
        ("#", "exit"),
    ]
    master, slave = pty.openpty()
    proc = subprocess.Popen(
        ["docker", "exec", "-i", "-t", container, "/pkg/bin/xr_cli.sh"],
        stdin=slave, stdout=slave, stderr=slave, close_fds=True,
    )
    os.close(slave)
    buf = b""
    idx = 0
    start = last_data = time.time()
    while time.time() - start < timeout:
        ready, _, _ = select.select([master], [], [], 0.2)
        if ready:
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            buf += chunk
            last_data = time.time()
        if idx < len(sends):
            wait_for, text = sends[idx]
            if wait_for is None or wait_for.encode() in buf:
                os.write(master, (text + "\n").encode())
                idx += 1
                buf = b""
        elif time.time() - last_data > idle_gap:
            break
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
    try:
        os.close(master)
    except OSError:
        pass
    return idx >= 4


def discover_nodes(prefix):
    ok, out, err = run(["docker", "ps", "--format", "{{.Names}}"])
    if not ok:
        print(f"[!] docker ps failed: {err}")
        sys.exit(1)
    names = [n for n in out.splitlines() if n.startswith(prefix)]
    return sorted(n[len(prefix):].lstrip("-") for n in names)


def save_node(prefix, node, outdir):
    container = f"{prefix}-{node}"
    disk_file = f"harddisk:/{node}-run.cfg"
    container_path = f"/misc/disk1/{node}-run.cfg"
    local_path = Path(outdir) / f"{node}.cfg"
    xr_cmd = f"show running-config | file {disk_file}"

    run(["docker", "exec", container, "rm", "-f", container_path])

    if not write_via_pty(container, xr_cmd):
        return node, False, "pty login/write did not complete"

    wrote, _, _ = run(["docker", "exec", container, "test", "-f", container_path])
    if not wrote:
        return node, False, "file not written (not saving stale data)"

    ok, out, err = run(["docker", "cp", f"{container}:{container_path}", str(local_path)])
    if not ok:
        return node, False, f"docker cp failed: {err}"

    if local_path.exists() and local_path.stat().st_size > 100:
        return node, True, f"{local_path.stat().st_size} bytes"
    return node, False, "saved file too small"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="clab-segment-routing-lab2")
    ap.add_argument("--nodes", nargs="*", default=None)
    ap.add_argument("--outdir", default="config")
    ap.add_argument("--workers", type=int, default=8,
                    help="Max parallel saves (default 8)")
    args = ap.parse_args()

    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    nodes = args.nodes or discover_nodes(args.prefix)
    if not nodes:
        print(f"[!] No running nodes for prefix '{args.prefix}'.")
        sys.exit(1)

    print(f"Saving configs for: {', '.join(nodes)} (parallel)\n")
    t0 = time.time()

    results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(save_node, args.prefix, n, args.outdir) for n in nodes]
        for f in futures:
            node, ok, msg = f.result()
            results[node] = ok
            mark = "[+]" if ok else "[!]"
            print(f"{mark} {node}: {msg}")

    ok_count = sum(results.values())
    dt = time.time() - t0
    print(f"\nDone: {ok_count}/{len(nodes)} saved to '{args.outdir}/' in {dt:.1f}s.")
    if ok_count < len(nodes):
        failed = [n for n, v in results.items() if not v]
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()