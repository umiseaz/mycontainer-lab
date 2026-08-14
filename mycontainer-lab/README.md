clab deploy -t clab-junos-mclag-arista-clab.yaml
clab inspect --all
sudo clab save -t clab-junos-mclag-arista-clab.yaml
clab destroy -t clab-junos-mclag-arista-clab.yaml


# junos
```
admin/admin@123
```

# arista
```
admin/admin
```

# cisco xrvd
```
clab/clab@123

# Save a router's live config to a file
show running-config | file harddisk:/r1-run.cfg

# Then from WSL, copy it out:

docker cp clab-segment-routing-lab1-r1:/misc/disk1/r1-run.cfg config/r1.cfg

# Verify it saved:
grep FORCE-R4 config/r1.cfg

# Test persistence (destroy + redeploy):

sudo containerlab destroy --cleanup -t segment-routing-lab1.yaml
sudo containerlab deploy -t segment-routing-lab1.yaml

# After ~4 min, log in and check it survived:
docker exec -it clab-segment-routing-lab1-r1 /pkg/bin/xr_cli.sh
show segment-routing traffic-eng policy

```

# not working
```
clab@DESKTOP-FTEM5HO:~/mycontainer-lab/segment-routing-lab1 (main)$ sudo containerlab save -t segment-routing-lab1.yaml
12:34:34 INFO Parsing & checking topology file=segment-routing-lab1.yaml
12:34:34 ERRO node "r1" save failed: failed to open netconf driver for clab-segment-routing-lab1-r1: dial tcp [3fff:172:20:20::3]:830: connect: connection refused
12:34:34 ERRO node "r3" save failed: failed to open netconf driver for clab-segment-routing-lab1-r3: dial tcp [3fff:172:20:20::5]:830: connect: connection refused
12:34:34 ERRO node "r2" save failed: failed to open netconf driver for clab-segment-routing-lab1-r2: dial tcp [3fff:172:20:20::4]:830: connect: connection refused
12:34:34 ERRO node "r4" save failed: failed to open netconf driver for clab-segment-routing-lab1-r4: dial tcp [3fff:172:20:20::2]:830: connect: connection refused
clab@DESKTOP-FTEM5HO:~/mycontainer-lab/segment-routing-lab1 (main)$ 
```