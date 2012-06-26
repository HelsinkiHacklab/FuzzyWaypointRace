import yaml
import sys,os
with open(os.path.realpath(__file__).replace('geopy_test.py', 'pocclient.yml')) as f:
    config = yaml.load(f)

import geopy, geopy.distance

numpoints = len(config['waypoints'])
for i1 in range(numpoints):
    for i2 in range(numpoints):
        if i1 == i2:
            continue
        p1 = config['waypoints'][i1]
        p2 = config['waypoints'][i2]
        
        gp1 = geopy.point.Point(p1['lat'], p1['lon'])
        gp2 = geopy.point.Point(p2['lat'], p2['lon'])
        
        dv = geopy.distance.VincentyDistance(gp1, gp2)
        dg = geopy.distance.GreatCircleDistance(gp1, gp2)
        
        print "%s <-> %s VincentyDistance: %s" % (p1['title'], p2['title'], dv)
        print "%s <-> %s GreatCircleDistance: %s" % (p1['title'], p2['title'], dg)
