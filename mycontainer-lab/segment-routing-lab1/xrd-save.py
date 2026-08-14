#!/usr/bin/env python3
"""
save_configs.py — Save running-config from all XRd nodes in a Containerlab lab.

Why this exists:
  The community sbezverk/xrd-control-plane image does NOT reliably expose SSH (22)
  or NetConf (830), so `containerlab save` and plain ssh both fail with
  "connection refused". The one method that always works is `docker exec` into
  the container and using XR's own "show running-config | file harddisk:/..."
  then copying the file out with `docker cp`.

  This script automates that for every node in the lab.

Usage:
  python3 save_configs.py
  python3 save_configs.py --prefix clab-segment-routing-lab1 --nodes r1 r2 r3 r4 --outdir config
"""

import argparse
import os
import pty
import select
import subprocess
import sys
import time
from pathlib import Path

# Default creds for this lab (see README.md). Only used as a fallback when
# the no-tty docker exec path below doesn't take (see save_node_via_pty).
XR_USER = "clab"
XR_PASS = "clab@123"


def run(cmd):
    """Run a shell command, return (ok, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()


def save_node_via_pty(container, xr_cmd, timeout=25, idle_gap=2.0):
    """Fallback for nodes where `docker exec -i xr_cli.sh` (no tty) fails with
    a 'tty-infra ... login_open failed' error. This has been observed to be
    flaky per-node on the sbezverk/xrd-control-plane image: some nodes accept
    the no-tty exec path, others reject it outright and only work through a
    real pty + interactive login. Drives that login with a real pty so it
    behaves like an interactive session.
    """
    sends = [
        (None, ""),
        ("Username:", XR_USER),
        ("Password:", XR_PASS),
        ("#", xr_cmd),
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
        ready, _, _ = select.select([master], [], [], 0.3)
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
    return idx == len(sends)


def discover_nodes(prefix):
    """Find running containers whose name starts with the lab prefix."""
    ok, out, err = run(["docker", "ps", "--format", "{{.Names}}"])
    if not ok:
        print(f"[!] docker ps failed: {err}")
        sys.exit(1)
    names = [n for n in out.splitlines() if n.startswith(prefix)]
    # strip the prefix + trailing dash to get short node names (r1, r2, ...)
    nodes = [n[len(prefix):].lstrip("-") for n in names]
    return sorted(nodes)


def save_node(prefix, node, outdir):
    """Save one node's running-config to outdir/<node>.cfg."""
    container = f"{prefix}-{node}"
    disk_file = f"harddisk:/{node}-run.cfg"
    container_path = f"/misc/disk1/{node}-run.cfg"
    local_path = Path(outdir) / f"{node}.cfg"

    # Step 1: tell XR to write its running-config to harddisk.
    # We feed the command into xr_cli.sh via a here-string over stdin.
    xr_cmd = f"show running-config | file {disk_file}"
    ok, out, err = run([
        "bash", "-c",
        f'echo "{xr_cmd}" | docker exec -i {container} /pkg/bin/xr_cli.sh'
    ])
    if "[OK]" not in out and "OK" not in out:
        # Not fatal on its own — some versions print nothing. Warn and continue.
        print(f"[~] {node}: write step returned no explicit OK "
              f"(continuing). Output: {out[:60]!r}")

    # Some nodes reject the no-tty exec path outright ('tty-infra ...
    # login_open failed'), so the file never gets written. Check for it and
    # fall back to a real pty + interactive login if it's missing.
    wrote, _, _ = run(["docker", "exec", container, "test", "-f", container_path])
    if not wrote:
        print(f"[~] {node}: no-tty write didn't take, retrying via pty login")
        if not save_node_via_pty(container, xr_cmd):
            print(f"[!] {node}: pty login fallback did not complete")
            return False

    # Step 2: copy the file out of the container to the local outdir.
    ok, out, err = run([
        "docker", "cp",
        f"{container}:{container_path}", str(local_path)
    ])
    if not ok:
        print(f"[!] {node}: docker cp failed: {err}")
        return False

    # Step 3: sanity check the file has real config in it.
    if local_path.exists() and local_path.stat().st_size > 100:
        size = local_path.stat().st_size
        print(f"[+] {node}: saved -> {local_path} ({size} bytes)")
        return True
    else:
        print(f"[!] {node}: saved file looks empty/too small")
        return False


def main():
    ap = argparse.ArgumentParser(description="Save XRd running-configs via docker exec.")
    ap.add_argument("--prefix", default="clab-segment-routing-lab1",
                    help="Container name prefix (default: clab-segment-routing-lab1)")
    ap.add_argument("--nodes", nargs="*", default=None,
                    help="Node short names (e.g. r1 r2 r3 r4). Auto-discovered if omitted.")
    ap.add_argument("--outdir", default="config",
                    help="Directory to write <node>.cfg files (default: config)")
    args = ap.parse_args()

    Path(args.outdir).mkdir(parents=True, exist_ok=True)

    nodes = args.nodes if args.nodes else discover_nodes(args.prefix)
    if not nodes:
        print(f"[!] No running nodes found for prefix '{args.prefix}'.")
        sys.exit(1)

    print(f"Saving configs for: {', '.join(nodes)}\n")

    results = {n: save_node(args.prefix, n, args.outdir) for n in nodes}

    ok_count = sum(results.values())
    print(f"\nDone: {ok_count}/{len(nodes)} nodes saved to '{args.outdir}/'.")
    if ok_count < len(nodes):
        failed = [n for n, v in results.items() if not v]
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()