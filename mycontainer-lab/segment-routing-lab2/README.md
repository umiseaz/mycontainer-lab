# segment-routing-lab2

7-node IS-IS + SR-MPLS lab designed so that a traffic-engineered path with
2+ intermediate waypoints keeps a real multi-label stack on the wire,
instead of collapsing to one label (which is what happened in lab1, where
every waypoint was a directly-connected neighbor of r1).

## Topology

```
  r1 --- r2 --- r3 --- r4 --- r5 --- r6
                 \                   /
                  \------ r7 -------/
```