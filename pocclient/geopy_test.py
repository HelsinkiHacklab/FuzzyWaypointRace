import yaml
import sys,os
with open(os.path.realpath(__file__).replace('geopy_test.py', 'pocclient.yml')) as f:
    config = yaml.load(f)

import geopy, geopy.distance


#Horisontal Bearing
def calcBearing(lat1, lon1, lat2, lon2):
    from math import *
    dLon = lon2 - lon1
    y = sin(dLon) * cos(lat2)
    x = cos(lat1) * sin(lat2) \
        - sin(lat1) * cos(lat2) * cos(dLon)
    return degrees(atan2(y, x)+pi)

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
        
        print "%s <-> %s VincentyDistance: %skm to %fdeg" % (p1['title'], p2['title'], dv.km, calcBearing(gp1[0],gp1[1],gp2[0],gp2[1]))
        print "%s <-> %s GreatCircleDistance: %skm to %fdeg" % (p1['title'], p2['title'], dg.km, calcBearing(gp1[0],gp1[1],gp2[0],gp2[1]))
