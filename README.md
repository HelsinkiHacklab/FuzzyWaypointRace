FuzzyWaypointRace
=================

The basic idea is that we have a set of waypoints that are known only to the race server, 
contestants can "ping" the server with their GPS coordinates and get back a list of distances to the waypoints,
these distances have a certain fuzz-factor (==random error) that depends on the scale of the distance
(so if you're close it might be tens of meters but if your far it might be or hundreds of km).

To get better estimate of the locations of the waypoints draw circles on the map after the ping (center on your location,
radius by distance), then move a bit (depending on the scale this might be several km) and ping again, draw another set of circles
and a pattern will start emerging.

Each ping gives a time penalty that is somehow based on the scale of the race (if we draw a circle around all 
the waypoints we can use the radius as base for that scale), if all waypoints are inside a smallish city (say Helsinki...)
then the penalty can be minutes but if the scale is something like whole of Finland then they need to be hours.

If the scale is suitable [GeoHash][1] points for the day can be used as one of the waypoints, this will be a published fact.
[Achievements][2] Can be used for time bonus.

Fastest time wins, this can be done either individually or as teams.

[1]: http://wiki.xkcd.com/geohashing/The_Algorithm
[2]: http://wiki.xkcd.com/geohashing/Achievements

Choosing the waypoints is a bit of a problem, either someone who is not participating does it manually or that we have a 
large list of waypoints and when creating a race the server will do a random selection inside a given circle of scale.  

For more "serious" races we need to make a simple "Ping device" that has GPS, GSM, SD-card, display and a simple MCU to tie
all this together, packaged so that tampering is evident, it will act as route tracker (store on SD) and by pressing a button a ping
can be sent and then the reply list of distances is shown on the display (these devices are identified by they GSM IMEI to the server)

## TODO

  1. Write a simple implementation of the "ping server", first just for local use for testing the all the fuzzing and scaling factors
  2. Write a simple ping visualizer where you can set your location on a map and the click "ping" and it will return you the distances and automatically draw the circles you use to
     determine the locations of the waypoints, this can actually have the whole "ping server" internalized since the only goal here is tune the
     scaling factors.
  3. Write a network ping server with some sort of multi-user registration (each ping request is hashed with a token given to the user), at first it will
     only run one race at a time, but needs to be extendable multiple races (ie multiple waypoint sets).
  4. Write Maemo/Meego/IOS/Android clients that will talk with the ping server (these clients will only return the list of distances, the visualization
     is not done for you [the point is that contestants a paper map and draw circles on it, or they could code their own visualizer...]), it
     will also keep local copy of your full GPS track for further reference.


