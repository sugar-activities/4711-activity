# forecastscreen.py
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
import logging

from datetime import datetime
from gettext import gettext as _

from sugar3.graphics import style
from sugar3.graphics.icon import Icon

SCREEN_WIDTH = Gdk.Screen.width()
SCREEN_HEIGHT = Gdk.Screen.height()

GREY = style.COLOR_PANEL_GREY.get_html()

_logger = logging.getLogger('weather-activity')

calendar = [_('Jan'), _('Feb'), _('Mar'), _('Apr'), _('May'), _('Jun'),
            _('Jul'), _('Aug'), _('Sep'), _('Oct'), _('Nov'), _('Dec')]

week = [_('Monday'), _('Tuesday'), _('Wednesday'), _('Thursday'),
        _('Friday'), _('Saturday'), _('Sunday')]

class ForecastDailyTreeView(Gtk.TreeView):
    def __init__(self, activity):
        Gtk.TreeView.__init__(self)
        
        self.activity = activity
        
        self.liststore = Gtk.ListStore(object)
        
        self.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property('height', SCREEN_HEIGHT / 10)
        
        renderer_pixbuf = Gtk.CellRendererPixbuf()
        
        column = Gtk.TreeViewColumn(_('Next days'), renderer_text)
        column.set_cell_data_func(renderer_text, self.load_date)
        column.set_min_width(SCREEN_WIDTH / 7)
        column.set_max_width(SCREEN_WIDTH / 7)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn('', renderer_pixbuf)
        column.set_cell_data_func(renderer_pixbuf, self.load_pixbuf)
        column.set_min_width(SCREEN_WIDTH / 9)
        column.set_max_width(SCREEN_WIDTH / 9)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn('', renderer_text)
        column.set_cell_data_func(renderer_text, self.load_info)
        column.set_min_width(SCREEN_WIDTH / 4)
        column.set_max_width(SCREEN_WIDTH / 4)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn(_('Wind'), renderer_text)
        column.set_cell_data_func(renderer_text, self.load_wind)
        column.set_min_width(SCREEN_WIDTH / 9)
        column.set_max_width(SCREEN_WIDTH / 9)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn(_('Clouds'), renderer_text)
        column.set_cell_data_func(renderer_text, self.load_clouds)
        column.set_min_width(SCREEN_WIDTH / 10)
        column.set_max_width(SCREEN_WIDTH / 10)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn(_('Pressure'), renderer_text)
        column.set_cell_data_func(renderer_text, self.load_pressure)
        column.set_min_width(SCREEN_WIDTH / 8)
        column.set_max_width(SCREEN_WIDTH / 8)
        self.append_column(column)
        
        column = Gtk.TreeViewColumn(_('Humidity'), renderer_text)
        column.set_cell_data_func(renderer_text, self.load_humidity)
        self.append_column(column)
        
        self.show()
        
    def load_date(self, column, cell_renderer, model, iter, data):
        forecast = model.get_value(iter, 0)
        timestamp = datetime.fromtimestamp(forecast['date'])
        date = '        %s %d' %(calendar[timestamp.month - 1], timestamp.day)
        cell_renderer.set_property('text', date)
    
    def load_pixbuf(self, column, cell_renderer, model, iter, data):
        cell_renderer.set_property('pixbuf', None)
        forecast = model.get_value(iter, 0)
        file_name = 'icons/%s.svg' % (forecast['icon'][:3])
        icon = GdkPixbuf.Pixbuf.new_from_file(file_name)
        cell_renderer.set_property('pixbuf', icon)
    
    def load_info(self, column, cell_renderer, model, iter, data):
        forecast = model.get_value(iter, 0)
        temp_day = self.activity.convert(forecast['temp_day'])
        temp_night = self.activity.convert(forecast['temp_night'])
            
        info = '<span foreground="black" background="#FFE578" \
            > %s%s </span>  <span foreground="white" background="#4264BA" \
            > %s%s </span>\n%s' % (temp_day, self.activity.temp_scale, 
            temp_night, self.activity.temp_scale, forecast['weather'])
            
        cell_renderer.set_property('markup', info)
    
    def load_wind(self, column, cell_renderer, model, iter, data):
        cell_renderer.set_property('text', '')
        forecast = model.get_value(iter, 0)
        if forecast['wind_speed'] != None:
            clouds = '\n%s %s' % (forecast['wind_speed'],
                                  self.activity.wind_scale)
            cell_renderer.set_property('text', clouds)
    
    def load_clouds(self, column, cell_renderer, model, iter, data):
        cell_renderer.set_property('text', '')
        forecast = model.get_value(iter, 0)
        if forecast['clouds'] != None:
            clouds = '\n    %s %s' % (int(forecast['clouds']),
                                      self.activity.cloud_scale)
            cell_renderer.set_property('text', clouds)
    
    def load_pressure(self, column, cell_renderer, model, iter, data):
        cell_renderer.set_property('text', '')
        forecast = model.get_value(iter, 0)
        if forecast['pressure'] != None:
            pressure = '\n%s %s' % (forecast['pressure'],
                                    self.activity.pressure_scale)
            cell_renderer.set_property('text', pressure)
    
    def load_humidity(self, column, cell_renderer, model, iter, data):
        cell_renderer.set_property('text', '')
        forecast = model.get_value(iter, 0)
        if forecast['humidity'] != None:
            humidity = '\n    %s %s' % (int(forecast['humidity']),
                                        self.activity.humidity_scale)
            cell_renderer.set_property('text', humidity)
    
    def update(self, city):
        self.set_model(None)
        self.liststore.clear()
        
        for forecast in city.forecast_daily:
            self.liststore.append([forecast])
            
        self.set_model(self.liststore)

class ForecastScreen(Gtk.Box):
    def __init__(self, activity):
        Gtk.Box.__init__(self)
        
        self.activity = activity
        
        self.name_label = Gtk.Label()
        self.name_label.set_alignment(0, 0)
        self.name_label.show()
        
        self.icon = Icon(pixel_size=SCREEN_HEIGHT / 4, 
                        fill_color=style.COLOR_TOOLBAR_GREY.get_svg())
        self.icon.show()
        
        self.temp_label = Gtk.Label()
        self.temp_label.show()
        
        self.temp_scale_label = Gtk.Label()
        self.temp_scale_label.set_alignment(0.33, 0.41)
        self.temp_scale_label.show()
        
        separator = Gtk.Separator()
        separator.set_property('expand', True)
        separator.modify_fg(Gtk.StateType.NORMAL,
                            Gdk.Color.parse(GREY)[1])
        separator.show()
        
        self.info_label = Gtk.Label()
        self.info_label.set_alignment(0, 0)
        self.info_label.set_margin_right(20)
        self.info_label.show()
        
        grid = Gtk.Grid()
        grid.attach(self.name_label, left=0, top=0, width=5, height=1)
        grid.attach(self.icon, left=0, top=1, width=1, height=2)
        grid.attach(self.temp_label, left=1, top=1, width=1, height=2)
        grid.attach(self.temp_scale_label, left=2, top=1, width=1, height=1)
        grid.attach(separator, left=3, top=1, width=1, height=1)
        grid.attach(self.info_label, left=4, top=1, width=1, height=2)
        grid.show()
        
        self.forecast_daily_treeview = ForecastDailyTreeView(self.activity)
        
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.forecast_daily_treeview)
        self.scroll.set_size_request(-1, SCREEN_HEIGHT / 2.2)
        self.scroll.show()
        
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.pack_start(grid, expand=True, fill=False, padding=0)
        self.pack_start(self.scroll, expand=False, fill=False, padding=0)
        
        self.show()
    
    def get_daily_forecast(self):
        city = self.activity.selected_city
        source = 'forecast/daily?id=%s&mode=json&cnt=7' % (city.id)
        dest = os.path.join(self.activity.get_activity_root(), 'tmp', 
                            '', str(city.id) + '.json')
        self.activity.add_download(source, dest)

    def download_complete(self, downloader, file_path, file_name):
        forecast = self.activity.read_file(file_path)['list']
        self.activity.selected_city.load_forecast_daily(forecast)
        self.activity.set_canvas(self)
    
    def refresh(self):
        self.activity.search_entry.set_text(self.activity.input)
        self.get_daily_forecast()
    
    def update_current(self, city):
        font_size = 28
        if len(city.name + city.country) > 20:
            font_size = 28 - (len(city.name + city.country) - 20)
            
        name = '<span font="Sans Bold %d">%s, %s\n</span>' % (
            font_size,
            city.name,
            city.country)
            
        timestamp = datetime.fromtimestamp(city.date)
        day = timestamp.weekday()
        time = '%02d:%02d' % (timestamp.hour, timestamp.minute)
        desc = '<span font="Sans 16">%s %s\n%s</span>' % (week[day], time,
                                                          city.weather)
            
        file_name = 'icons/%s.svg' % (city.icon[:3])
        self.icon.hide()
        self.icon.set_file(file_name)
        self.icon.show()
            
        temp = self.activity.convert(city.temp)
        degree = '<span stretch="ultracondensed" font="Sans 40"> %s</span>'\
                 % (temp)
        scale = '<span font="Sans 16">%s</span>' % (self.activity.temp_scale)
            
        wind = _('Wind') + ': '
        if city.wind_speed != None:
            wind = wind + '%s %s' % (city.wind_speed,
                                     self.activity.wind_scale)
            
        clouds = _('Clouds') + ': '
        if city.clouds != None:
            clouds = clouds + '%s %s' % (int(city.clouds),
                                         self.activity.cloud_scale)
            
        pressure = _('Pressure') + ': '
        if city.pressure != None:
            pressure = pressure + '%s %s' % (city.pressure,
                                             self.activity.pressure_scale)
            
        humidity = _('Humidity') + ': '
        if city.humidity != None:
            humidity = humidity + '%s %s' % (int(city.humidity),
                                             self.activity.humidity_scale)
            
        info = '<span font="Sans 16">%s\n%s\n%s\n%s</span>' % (wind, clouds, 
                                                               pressure, 
                                                               humidity)
            
        self.name_label.set_markup(name + desc)
        self.temp_label.set_markup(degree)
        self.temp_scale_label.set_markup(scale)
        self.info_label.set_markup(info)
    
    def display_results(self):
        city = self.activity.selected_city
        if city:
            self.update_current(city)
            self.forecast_daily_treeview.update(city)

    