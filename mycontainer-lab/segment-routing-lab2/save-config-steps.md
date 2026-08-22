# Saving XRd Configs in Containerlab — Two Methods

The community `sbezverk/xrd-control-plane:7.9.2` image does NOT reliably expose
SSH (22) or NetConf (830), so `containerlab save` and plain `ssh` fail with
"connection refused". Config is safe on the router while it runs, but is lost on
`destroy --cleanup` unless saved to the `config/*.cfg` files.

Two ways to save: the script (fast, all nodes) or manual (one node, no script).

---

## Method 1 — Script (fast, all nodes)

```bash
cd /home/clab/mycontainer-lab/segment-routing-lab2/
python3 xrd-save.py
```

- Saves all nodes in parallel (~10-15s for 7 nodes).
- Auto-discovers nodes by prefix. Override with `--prefix` if needed:
  ```bash
  python3 xrd-save.py --prefix clab-segment-routing-lab2 --outdir config
  ```
- Deletes the stale harddisk file before writing, so it can never save old config.
- Reports `[+] saved` per node, or `[!]` if a node failed (and skips it, not stale).

Verify configs are fresh (today's date):
```bash
grep -l "$(date '+%b %-d')" config/*.cfg
```

---

## Method 2 — Manual (one node, no script)

Use this when the script isn't available, or to save a single node.

### Step 1 — log into the node
```bash
docker exec -it clab-segment-routing-lab2-r1 /pkg/bin/xr_cli.sh
```
User: `clab`  Password: `clab@123`

### Step 2 — write running-config to the router's disk
At the `RP/0/RP0/CPU0:r1#` prompt:
```
show running-config | file harddisk:/r1-run.cfg
```
- If it asks `Save: File exists, overwrite ?[confirm]` — press Enter.
- Wait for `[OK]`.
Then:
```
exit
```

### Step 3 — copy the file out to the config folder
```bash
docker cp clab-segment-routing-lab2-r1:/misc/disk1/r1-run.cfg config/r1.cfg
```

### Step 4 — verify it's fresh
```bash
head -3 config/r1.cfg
```
Check `Last configuration change` shows today's date, not an old one.

Repeat Steps 1-4 for each node (change r1 → r2, r3, ... in both the container
name and the filename).

---

## Key notes

- **File path inside the container:** `/misc/disk1/`
- **Credentials:** `clab` / `clab@123`
- **`docker exec ... -c "show ..."` does NOT work** on this image (bash splits the
  argument). Always use interactive `xr_cli.sh` or the script.
- **`containerlab save` does NOT work** — NetConf chunked-framing bug between
  containerlab 0.78.2 and this XRd image.
- **Persistence rule:** config in `config/*.cfg` + `startup-config:` in the YAML
  survives `destroy --cleanup`. Live-only config is lost on cleanup.
- **Always save before `destroy --cleanup`** if you made live changes.

---

## Quick reference — commands

| Task | Command |
|------|---------|
| Save all nodes (fast) | `python3 xrd-save.py` |
| Log into a node | `docker exec -it clab-segment-routing-lab2-rX /pkg/bin/xr_cli.sh` |
| Write config to disk (in CLI) | `show running-config \| file harddisk:/rX-run.cfg` |
| Copy config out | `docker cp clab-segment-routing-lab2-rX:/misc/disk1/rX-run.cfg config/rX.cfg` |
| Verify fresh | `head -3 config/rX.cfg` |
| Deploy | `sudo containerlab deploy -t segment-routing-lab2.yaml` |
| Destroy (keep config) | `sudo containerlab destroy -t segment-routing-lab2.yaml` |
| Destroy (wipe) | `sudo containerlab destroy --cleanup -t segment-routing-lab2.yaml` |