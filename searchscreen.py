# searchscreen.py
#
# Copyright (C) 2013 Matthew Rahing
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General
# Public License as published by the Free Software
# Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General
# Public License along with this program; if not, write
# to the Free Software Foundation, Inc., 51 Franklin
# St, Fifth Floor, Boston, MA 02110-1301  USA

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

import os
import openweathermap
import logging

from gettext import gettext as _

SCREEN_WIDTH = Gdk.Screen.width()
SCREEN_HEIGHT = Gdk.Screen.height()

_logger = logging.getLogger('weather-activity')

class SearchTreeView(Gtk.TreeView):
    def __init__(self, activity):
        Gtk.TreeView.__init__(self)
        
        self.activity = activity
        
        self.liststore = Gtk.ListStore(object)
        
        self.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        
        renderer_pixbuf = Gtk.CellRendererPixbuf()
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property('height', SCREEN_HEIGHT / 10)
        
        column = Gtk.TreeViewColumn('', renderer_pixbuf)
        column.set_cell_data_func(renderer_pixbuf, self.load_pixbuf)
        column.set_min_width(SCREEN_WIDTH / 9)
        column.set_max_width(SCREEN_WIDTH / 9)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn('', renderer_text)
        column.set_cell_data_func(renderer_text, self.load_info)
        column.set_min_width(SCREEN_WIDTH / 2.6)
        column.set_max_width(SCREEN_WIDTH / 2.6)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn(_('Wind'), renderer_text)
        column.set_cell_data_func(renderer_text, self.load_wind)
        column.set_min_width(SCREEN_WIDTH / 8)
        column.set_max_width(SCREEN_WIDTH / 8)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn(_('Clouds'), renderer_text)
        column.set_cell_data_func(renderer_text, self.load_clouds)
        column.set_min_width(SCREEN_WIDTH / 9)
        column.set_max_width(SCREEN_WIDTH / 9)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn(_('Pressure'), renderer_text)
        column.set_cell_data_func(renderer_text, self.load_pressure)
        column.set_min_width(SCREEN_WIDTH / 7)
        column.set_max_width(SCREEN_WIDTH / 7)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn(_('Humidity'), renderer_text)
        column.set_cell_data_func(renderer_text, self.load_humidity)
        self.append_column(column)
        
        self.set_model(self.liststore)
        
        selection = self.get_selection()
        selection.connect('changed', self.treeview_changed)
        
        self.show()
    
    def load_pixbuf(self, column, cell_renderer, model, iter, data):
        city = model.get_value(iter, 0)
        
        file_name = 'icons/%s.svg' % (city.icon[:3])
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_name)
        
        cell_renderer.set_property('pixbuf', pixbuf)
    
    def load_info(self, column, cell_renderer, model, iter, data):
        city = model.get_value(iter, 0)
        
        name = '%s, %s' % (city.name, city.country)
        temp = self.activity.convert(city.temp)
        temp_max = self.activity.convert(city.temp_max)
        temp_min = self.activity.convert(city.temp_min)
        
        info = '<b>%s</b> %s\n<span foreground="white" background="#5FACE0" \
                > %s%s </span> Temp from %s%s to %s%s' % (name, city.weather, 
                temp, self.activity.temp_scale,
                temp_min, self.activity.temp_scale,
                temp_max, self.activity.temp_scale)
                
        cell_renderer.set_property('markup', info)
    
    def load_wind(self, column, cell_renderer, model, iter, data):
        cell_renderer.set_property('text', '')
        city = model.get_value(iter, 0)
        if city.wind_speed != None:
            wind = '\n%s %s' % (city.wind_speed, self.activity.wind_scale)
            cell_renderer.set_property('text', wind)
    
    def load_clouds(self, column, cell_renderer, model, iter, data):
        cell_renderer.set_property('text', '')
        city = model.get_value(iter, 0)
        if city.clouds != None:
            clouds = '\n   %s %s' % (int(city.clouds), 
                                    self.activity.cloud_scale)
            cell_renderer.set_property('text', clouds)

    def load_pressure(self, column, cell_renderer, model, iter, data):
        cell_renderer.set_property('text', '')
        city = model.get_value(iter, 0)
        if city.pressure != None:
            pressure = '\n%s %s' % (city.pressure, 
                                   self.activity.pressure_scale)
            cell_renderer.set_property('text', pressure)
    
    def load_humidity(self, column, cell_renderer, model, iter, data):
        cell_renderer.set_property('text', '')
        city = model.get_value(iter, 0)
        if city.humidity != None:
            humidity = '\n   %s %s' % (int(city.humidity), 
                                      self.activity.humidity_scale)
            cell_renderer.set_property('text', humidity)
    
    def treeview_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            self.activity.select_city(model[treeiter][0])
    
    def update(self, results):
        self.set_model(None)
        self.liststore.clear()
        
        for city in results:
            self.liststore.append([city])
        
        self.set_model(self.liststore)

class SearchScreen(Gtk.Box):
    def __init__(self, activity):
        Gtk.Box.__init__(self)
        
        self.activity = activity
        self.search_results = []
        
        self.search_treeview = SearchTreeView(self.activity)
        
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.search_treeview)
        self.scroll.show()
        
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.pack_start(self.scroll, expand=True, fill=True, padding=0)
        
        self.show()
    
    def search(self):
        _logger.debug('searching: %s' % (self.activity.input))
        source = 'find?q=%s&type=like&mode=json' % (self.activity.input)
        dest = os.path.join(self.activity.get_activity_root(), 
                            'tmp', '', 'search.json')
        self.activity.add_download(source, dest)

    def download_complete(self, downloader, file_path, file_name):
        self.search_results = []
        for result in self.activity.read_file(file_path)['list']:
            self.search_results.append(openweathermap.City(result))
            
        self.activity.back_button.set_sensitive(False)
        self.activity.forecast_button.set_sensitive(False)
        
        self.activity.set_canvas(self)

    def refresh(self):
        self.activity.search_entry.set_text(self.activity.input)
        self.search()
    
    def display_results(self):
        self.search_treeview.update(self.search_results)

