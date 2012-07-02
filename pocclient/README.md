Proof of Concept -Client
========================

Used to test the scaling and fuzzing functions, basic idea is that the waypoints are configured to a known set (and visibility toggleable).

The map works pretty much as expected, drag to move around, left-click centers the map, scrollwheel zooms. Right click pings the server and
draws the distances as circles (the center point is also maked with a "radio tower" icon).

Currently 5% linear fuzzing seems a reasonable value.

The colors need a bit of thinking, I tried to get good contrasting colors from a colorwheel but it seems OSM uses very similar colorshceme.
