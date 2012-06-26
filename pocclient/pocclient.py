#!/usr/bin/python
from __future__ import with_statement
import yaml
import os,sys
libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..', 'lib')
if os.path.isdir(libs_dir):                                       
    sys.path.append(libs_dir)
import geopy, geopy.distance


"""
Copyright (C) Hadley Rich 2008 <hads@nice.net.nz>
based on main.c - with thanks to John Stowers

This is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

import sys
import os.path
import gtk.gdk
import gobject

gobject.threads_init()
gtk.gdk.threads_init()

#Try static lib first
mydir = os.path.dirname(os.path.abspath(__file__))
libdir = os.path.abspath(os.path.join(mydir, "..", "python", ".libs"))
sys.path.insert(0, libdir)

import osmgpsmap
print "using library: %s (version %s)" % (osmgpsmap.__file__, osmgpsmap.__version__)

assert osmgpsmap.__version__ == "0.7.2"

class DummyMapNoGpsPoint(osmgpsmap.GpsMap):
    def do_draw_gps_point(self, drawable):
        pass
gobject.type_register(DummyMapNoGpsPoint)

class DummyLayer(gobject.GObject, osmgpsmap.GpsMapLayer):
    def __init__(self):
        gobject.GObject.__init__(self)

    def do_draw(self, gpsmap, gdkdrawable):
        pass

    def do_render(self, gpsmap):
        pass

    def do_busy(self):
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        return False
gobject.type_register(DummyLayer)

# stolen from https://gramps.svn.sourceforge.net/svnroot/gramps/trunk/src/plugins/lib/maps/selectionlayer.py
class SelectionLayer(gobject.GObject, osmgpsmap.GpsMapLayer):
    def __init__(self):
        """
        Initialize thz selection layer
        """
        gobject.GObject.__init__(self)
        self.circles = []
        self.rectangles = []

    def add_circle(self, rds, lat, lon):
        """
        Add a circle
        """
        self.circles.append((rds, lat, lon))

    def add_rectangle(self, cp1, cp2):
        """
        Add a rectangle
        """
        self.rectangles.append((cp1, cp2))

    def do_draw(self, gpsmap, drawable):
        """
        draw the circles and the rectangles
        """
        ggc = drawable.new_gc()
        for circle in self.circles:
# The radius in degreees messes stuff up when being a bit farther rom equator            
#            top_left = osmgpsmap.point_new_degrees(circle[1] + circle[0],
#                                                   circle[2] - circle[0])
#            bottom_right = osmgpsmap.point_new_degrees(circle[1] - circle[0],
#                                                       circle[2] + circle[0])
#            crd_x, crd_y = gpsmap.convert_geographic_to_screen(top_left)
#            crd_x2, crd_y2 = gpsmap.convert_geographic_to_screen(bottom_right)
#            drawable.draw_arc(ggc, False, crd_x, crd_y, crd_x2 - crd_x,
#                              crd_y2 - crd_y, 0, 360*64)
            # TODO: Calculate four "corners" (n,e,s,w) of the ellipse by distance, use proj to switch between projections if neccessary
            d = geopy.distance.VincentyDistance(kilometers=circle[0])
            center = geopy.point.Point(circle[1], circle[2])
            np = d.destination(center, 0)
            ep = d.destination(center, 90)
            sp = d.destination(center, 180)
            wp = d.destination(center, 270)
            osm_np = osmgpsmap.point_new_degrees(np[0], np[1])
            osm_ep = osmgpsmap.point_new_degrees(ep[0], ep[1])
            osm_sp = osmgpsmap.point_new_degrees(sp[0], sp[1])
            osm_wp = osmgpsmap.point_new_degrees(wp[0], wp[1])
            
            view_np = gpsmap.convert_geographic_to_screen(osm_np)
            view_ep = gpsmap.convert_geographic_to_screen(osm_ep)
            view_sp = gpsmap.convert_geographic_to_screen(osm_sp)
            view_wp = gpsmap.convert_geographic_to_screen(osm_wp)

            # TODO: There probably is a better way to calculate these but I don't care, this works now
            drawable.draw_arc(ggc, False, view_wp[0], view_np[1], (view_ep[0] - view_wp[0]), (view_sp[1] - view_np[1]), 0, 360*64)


        for rectangle in self.rectangles:
            top_left, bottom_right = rectangle
            crd_x, crd_y = gpsmap.convert_geographic_to_screen(top_left)
            crd_x2, crd_y2 = gpsmap.convert_geographic_to_screen(bottom_right)
            # be sure when can select a region in all case.
            if ( crd_x < crd_x2 ):
                if ( crd_y < crd_y2 ):
                    drawable.draw_rectangle(ggc, False, crd_x, crd_y,
                                            crd_x2 - crd_x, crd_y2 - crd_y)
                else:
                    drawable.draw_rectangle(ggc, False, crd_x, crd_y2,
                                            crd_x2 - crd_x, crd_y - crd_y2)
            else:
                if ( crd_y < crd_y2 ):
                    drawable.draw_rectangle(ggc, False, crd_x2, crd_y,
                                            crd_x - crd_x2, crd_y2 - crd_y)
                else:
                    drawable.draw_rectangle(ggc, False, crd_x2, crd_y2,
                                            crd_x - crd_x2, crd_y - crd_y2)

    def do_render(self, gpsmap):
        """
        render the layer
        """
        pass

    def do_busy(self):
        """
        set the map busy
        """
        return False

    def do_button_press(self, gpsmap, gdkeventbutton):
        """
        Someone press a button
        """
        return False

gobject.type_register(SelectionLayer)



class UI(gtk.Window):
    def __init__(self, config):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.config = config

        self.set_default_size(500, 500)
        self.connect('destroy', lambda x: gtk.main_quit())
        self.set_title('OpenStreetMap GPS Mapper')

        self.vbox = gtk.VBox(False, 0)
        self.add(self.vbox)

        # WTF is this here for ??
        if 0:
            self.osm = DummyMapNoGpsPoint()
        else:
            self.osm = osmgpsmap.GpsMap()
#        self.osm.layer_add(
#                    osmgpsmap.GpsMapOsd(
#                        show_dpad=True,
#                        show_zoom=True))
        self.osm.layer_add(
                    DummyLayer())

        self.sl = SelectionLayer()
        self.osm.layer_add(self.sl)

        self.osm.connect('button_release_event', self.map_clicked)

        #connect keyboard shortcuts
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_FULLSCREEN, gtk.gdk.keyval_from_name("F11"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_UP, gtk.gdk.keyval_from_name("Up"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_DOWN, gtk.gdk.keyval_from_name("Down"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_LEFT, gtk.gdk.keyval_from_name("Left"))
        self.osm.set_keyboard_shortcut(osmgpsmap.KEY_RIGHT, gtk.gdk.keyval_from_name("Right"))

        #connect to tooltip
        self.osm.props.has_tooltip = True
        self.osm.connect("query-tooltip", self.on_query_tooltip)

        self.latlon_entry = gtk.Entry()
        self.radius_entry = gtk.Entry()
        self.radius_entry.set_text("0.1")

        zoom_in_button = gtk.Button(stock=gtk.STOCK_ZOOM_IN)
        zoom_in_button.connect('clicked', self.zoom_in_clicked)
        zoom_out_button = gtk.Button(stock=gtk.STOCK_ZOOM_OUT)
        zoom_out_button.connect('clicked', self.zoom_out_clicked)
        home_button = gtk.Button(stock=gtk.STOCK_HOME)
        home_button.connect('clicked', self.home_clicked)
#        cache_button = gtk.Button('Cache')
#        cache_button.connect('clicked', self.cache_clicked)
        wp_button = gtk.Button('Waypoints')
        wp_button.connect('clicked', self.toggle_waypoints)

        self.vbox.pack_start(self.osm)
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(zoom_in_button)
        hbox.pack_start(zoom_out_button)
        hbox.pack_start(home_button)
#        hbox.pack_start(cache_button)
        hbox.pack_start(wp_button)

        #add ability to test custom map URIs
        ex = gtk.Expander("<b>Map Repository URI</b>")
        ex.props.use_markup = True
        vb = gtk.VBox()
        self.repouri_entry = gtk.Entry()
        self.repouri_entry.set_text(self.osm.props.repo_uri)
        self.image_format_entry = gtk.Entry()
        self.image_format_entry.set_text(self.osm.props.image_format)

        lbl = gtk.Label(
"""
Enter an repository URL to fetch map tiles from in the box below. Special metacharacters may be included in this url

<i>Metacharacters:</i>
\t#X\tMax X location
\t#Y\tMax Y location
\t#Z\tMap zoom (0 = min zoom, fully zoomed out)
\t#S\tInverse zoom (max-zoom - #Z)
\t#Q\tQuadtree encoded tile (qrts)
\t#W\tQuadtree encoded tile (1234)
\t#U\tEncoding not implemeted
\t#R\tRandom integer, 0-4""")
        lbl.props.xalign = 0
        lbl.props.use_markup = True
        lbl.props.wrap = True

        ex.add(vb)
        vb.pack_start(lbl, False)

        hb = gtk.HBox()
        hb.pack_start(gtk.Label("URI: "), False)
        hb.pack_start(self.repouri_entry, True)
        vb.pack_start(hb, False)

        hb = gtk.HBox()
        hb.pack_start(gtk.Label("Image Format: "), False)
        hb.pack_start(self.image_format_entry, True)
        vb.pack_start(hb, False)

        gobtn = gtk.Button("Load Map URI")
        gobtn.connect("clicked", self.load_map_clicked)
        vb.pack_start(gobtn, False)

        self.show_tooltips = False
        cb = gtk.CheckButton("Show Location in Tooltips")
        cb.props.active = self.show_tooltips
        cb.connect("toggled", self.on_show_tooltips_toggled)
        self.vbox.pack_end(cb, False)

        cb = gtk.CheckButton("Disable Cache")
        cb.props.active = False
        cb.connect("toggled", self.disable_cache_toggled)
        self.vbox.pack_end(cb, False)

        self.vbox.pack_end(ex, False)
        self.vbox.pack_end(self.latlon_entry, False)
        self.vbox.pack_end(self.radius_entry, False)
        self.vbox.pack_end(hbox, False)

        gobject.timeout_add(100, self.home_clicked, None)
        gobject.timeout_add(500, self.print_tiles)
        self.waypoints = None
        self.marker_cache = {}

    def disable_cache_toggled(self, btn):
        if btn.props.active:
            self.osm.props.tile_cache = osmgpsmap.CACHE_DISABLED
        else:
            self.osm.props.tile_cache = osmgpsmap.CACHE_AUTO

    def on_show_tooltips_toggled(self, btn):
        self.show_tooltips = btn.props.active

    def load_map_clicked(self, button):
        uri = self.repouri_entry.get_text()
        format = self.image_format_entry.get_text()
        if uri and format:
            if self.osm:
                #remove old map
                self.vbox.remove(self.osm)
            try:
                self.osm = osmgpsmap.GpsMap(
                    repo_uri=uri,
                    image_format=format
                )
            except Exception, e:
                print "ERROR:", e
                self.osm = osmgpsmap.GpsMap()

            self.vbox.pack_start(self.osm, True)
            self.osm.connect('button_release_event', self.map_clicked)
            self.osm.show()


    def toggle_waypoints(self, *args):
        if self.waypoints:
            for img in self.waypoints:
                self.osm.image_remove(img)
            self.waypoints = None
            return
        self.waypoints = []
        for wp in self.config['waypoints']:
            img = self.add_marker('pin', wp['lat'], wp['lon'])
            self.waypoints.append(img)

    def print_tiles(self):
        if self.osm.props.tiles_queued != 0:
            print self.osm.props.tiles_queued, 'tiles queued'
        return True

    def zoom_in_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom + 1)
 
    def zoom_out_clicked(self, button):
        self.osm.set_zoom(self.osm.props.zoom - 1)

    def home_clicked(self, button):
        home = self.config['home']
        self.osm.set_center_and_zoom(home['lat'], home['lon'], home['zoom'])

    def on_query_tooltip(self, widget, x, y, keyboard_tip, tooltip, data=None):
        if keyboard_tip:
            return False

        if self.show_tooltips:
            p = osmgpsmap.point_new_degrees(0.0, 0.0)
            self.osm.convert_screen_to_geographic(x, y, p)
            lat,lon = p.get_degrees()
            tooltip.set_markup("%+.4f, %+.4f" % p.get_degrees())
            return True

        return False
 
    def cache_clicked(self, button):
        bbox = self.osm.get_bbox()
        self.osm.download_maps(
            *bbox,
            zoom_start=self.osm.props.zoom,
            zoom_end=self.osm.props.max_zoom
        )


    def add_marker(self, marker_id, lat, lon):
        marker = self.config['markers'][marker_id]
        if not self.marker_cache.has_key(marker_id):
            self.marker_cache[marker_id] = gtk.gdk.pixbuf_new_from_file_at_size (marker['file'], marker['size'][0],marker['size'][1])
        return self.osm.image_add_with_alignment(lat,lon,self.marker_cache[marker_id],marker['offset'][0],marker['offset'][1])

    def map_clicked(self, osm, event):
        lat,lon = self.osm.get_event_location(event).get_degrees()
        if event.button == 1:
            self.osm.set_center(lat,lon)
            self.latlon_entry.set_text(
                'Map Centre: latitude %s longitude %s' % (
                    self.osm.props.latitude,
                    self.osm.props.longitude
                )
            )
        elif event.button == 2:
            self.osm.gps_add(lat, lon, heading=osmgpsmap.INVALID);
        elif event.button == 3:
            ##self.add_marker('pin', lat, lon)
            self.add_marker('beacon', lat, lon)
            rds = float(self.radius_entry.get_text().replace(',', '.'))
            self.sl.add_circle(rds, lat, lon)
            

if __name__ == "__main__":
    with open(os.path.realpath(__file__).replace('.py', '.yml')) as f:
        config = yaml.load(f)
    u = UI(config)
    u.show_all()
    if os.name == "nt": gtk.gdk.threads_enter()
    gtk.main()
    if os.name == "nt": gtk.gdk.threads_leave()
