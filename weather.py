# weather.py    Weather Forecast
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

import json
import gobject
import logging
import searchscreen
import forecastscreen

from fractions import Fraction
from gettext import gettext as _

from sugar3 import network

from sugar3.activity import activity
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton

from sugar3.graphics import style
from sugar3.graphics import iconentry
from sugar3.graphics.alert import ConfirmationAlert
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolcombobox import ToolComboBox
from sugar3.graphics.toolbarbox import ToolbarButton

_logger = logging.getLogger('weather-activity')

SCREEN_WIDTH = Gdk.Screen.width()
SCREEN_HEIGHT = Gdk.Screen.height()

GREY = style.COLOR_PANEL_GREY.get_html()

howto = _('Enter the city\'s name to get a list of the most proper cities in \
the world. \nIf you put a more precise name, you will get a more precise list.\
\nExample - <b>Lon</b> or <b>Lond</b> or <b>London</b>.')

class ReadURLDownloader(network.GlibURLDownloader):
    """URLDownloader that provides content-length and content-type."""
    
    CHUNK_SIZE = 32

    def get_content_length(self):
        """Return the content-length of the download."""
        if self._info is not None:
            try:
                return int(self._info.headers.get('Content-Length'))
            except TypeError:
                return 50

    def get_content_type(self):
        """Return the content-type of the download."""
        if self._info is not None:
            return self._info.headers.get('Content-Type')
        return None


class WeatherActivity(activity.Activity):
    """WeatherActivity class as specified in activity.info"""

    def __init__(self, handle):
        """Set up the Weather activity."""
        activity.Activity.__init__(self, handle)
        
        # we do not have collaboration features
        # make the share option insensitive
        self.max_participants = 1
        
        self.wind_scale = 'm/s'
        self.pressure_scale = 'hPa'
        self.humidity_scale = '%'
        self.cloud_scale = '%'
        self.temp_scale = 'K'
        self.input = ''
        self.selected_city = None
        
        self.temp_scales = {'Kelvin' : 'K',
                            'Celcius' : u'\u00b0C'.encode('utf-8'),
                            'Farenheit' : u'\u00b0F'.encode('utf-8')}
        
        # view toolbar
        view_toolbar = Gtk.Toolbar()
        toolbar_box = ToolbarBox()
        
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()
        
        temp_label = Gtk.Label(_('Temperature:'))
        temp_label.show()
        
        temp_label_item = Gtk.ToolItem()
        temp_label_item.add(temp_label)
        temp_label_item.show()
        
        temp_scale_store = Gtk.ListStore(str)
        for key in self.temp_scales.keys():
            temp_scale_store.append([key])
        
        self.temp_scale_combo = Gtk.ComboBox.new_with_model(temp_scale_store)
        renderer_text = Gtk.CellRendererText()
        self.temp_scale_combo.pack_start(renderer_text, True)
        self.temp_scale_combo.add_attribute(renderer_text, 'text', 0)
        self.temp_scale_combo.connect('changed', self.temp_scale_combo_toggled)
        self.temp_scale_combo.show()
        
        temp_scale_combo_item = ToolComboBox(self.temp_scale_combo)
        temp_scale_combo_item.show()
        
        view_toolbar.insert(temp_label_item, -1)
        view_toolbar.insert(temp_scale_combo_item, -1)
        view_toolbar.show()
        
        view_toolbar_button = ToolbarButton(icon_name='toolbar-view', 
                                            page=view_toolbar)
        toolbar_box.toolbar.insert(view_toolbar_button, -1)
        view_toolbar_button.show()
        
        # toolbar
        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)
        separator.set_draw(False)
        separator.set_expand(True)
        separator.show()
        
        self.search_entry = iconentry.IconEntry()
        self.search_entry.connect('key-press-event', self.entry_key_press_cb)
        self.search_entry.connect('icon-press', self.refresh)
        self.search_entry.show()
        
        self.search_entry_item = Gtk.ToolItem()
        self.search_entry_item.set_size_request(SCREEN_WIDTH / 3, -1)
        self.search_entry_item.add(self.search_entry)
        toolbar_box.toolbar.insert(self.search_entry_item, -1)
        self.search_entry_item.show()
        
        self.back_button = ToolButton('go-previous-paired')
        self.back_button.connect('clicked', self.back_button_clicked)
        self.back_button.set_sensitive(False)
        self.back_button.set_tooltip(_('Back'))
        toolbar_box.toolbar.insert(self.back_button, -1)
        self.back_button.show()
        
        self.forecast_button = ToolButton('go-next-paired')
        self.forecast_button.connect('clicked', self.forecast_button_clicked)
        self.forecast_button.set_sensitive(False)
        self.forecast_button.set_tooltip(_('Forecast'))
        toolbar_box.toolbar.insert(self.forecast_button, -1)
        self.forecast_button.show()
        
        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)
        separator.set_draw(False)
        separator.set_expand(True)
        separator.show()
        
        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()
        
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()
        
        # set up screen
        self.search_screen = searchscreen.SearchScreen(self)
        self.forecast_screen = forecastscreen.ForecastScreen(self)
        
        self.screen = self.search_screen
        
        howto_label = Gtk.Label()
        howto_label.set_justify(Gtk.Justification.CENTER)
        howto_label.set_markup(howto)
        howto_label.show()
        
        world_image = Gtk.Image()
        world_image.modify_bg(Gtk.StateType.NORMAL, 
                              Gdk.Color.parse(GREY)[1])
        pixbuf = GdkPixbuf.Pixbuf.new_from_file('world.svg')
        scaled_pixbuf = pixbuf.scale_simple(SCREEN_WIDTH, SCREEN_HEIGHT - 170, 
                                            GdkPixbuf.InterpType.BILINEAR)
        world_image.set_from_pixbuf(scaled_pixbuf)
        world_image.show()
        
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.pack_start(howto_label, expand=True, fill=False, padding=0)
        box.pack_start(world_image, expand=True, fill=True, padding=0)
        box.show()
        
        self.set_canvas(box)
        
        self.temp_scale_combo.set_active(1)
        self.search_entry.grab_focus()
    
    def _alert_confirmation(self):
        alert = ConfirmationAlert()
        alert.remove_button(Gtk.ResponseType.CANCEL)
        alert.props.title = (_('Download Error'))
        alert.props.msg = (_('There was a problem with the download'))
        alert.connect('response', self._alert_response)
        self.add_alert(alert)
    
    def _alert_response(self, alert, response_id):
        self.remove_alert(alert)
    
    def entry_key_press_cb(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Return':
            self.set_focus(None)
            self.input = widget.get_text()
            
            self.search_screen.search()
            
            self.screen = self.search_screen
    
    def read_file(self, file):
        data = open(file, 'r')
        try:
            text = data.read()
            dict = json.loads(text)
            return dict
        finally:
            data.close()
    
    def add_download(self, source, dest):
        self.search_entry.set_progress_fraction(0.2)
        gobject.idle_add(self.download, source, dest)

    def download(self, source, dest):
        id = '43ae262450afb936759b9e905323c7e5'
        url = 'http://api.openweathermap.org/data/2.5/%s&APPID=%s' % (source,
                                                                      id)
        _logger.debug(url)
        downloader = ReadURLDownloader(url)
        
        downloader.connect("error", self._alert_confirmation)
        downloader.connect("progress", self.get_download_progress)
        downloader.connect("finished", self.download_complete)
        
        try:
            downloader.start(dest)
            
        except:
            _logger.debug('download error')
            self._alert_confirmation()
        
        self.download_size = downloader.get_content_length()
        self.download_type = downloader.get_content_type()
        _logger.debug('size ' + str(self.download_size))
        _logger.debug('type ' + str(self.download_type) + '\n')

    def download_complete(self, downloader, file_path, file_name):
        self.search_entry.set_progress_fraction(0)
        file_type = self.download_type
        
        if file_type.startswith('text/html') or self.download_size < 1:
            _logger.debug('corrupt download')
            self._alert_confirmation()
        else:
            if self.read_file(file_path)['cod'] == '200':
                self.screen.download_complete(downloader, file_path, file_name)
                
            self.screen.display_results()
            self.show_refresh_button()
    
    def get_download_progress(self, downloader, bytes_downloaded):
        if self.download_size:
            self.update_progressbar(bytes_downloaded,  self.download_size)
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    def update_progressbar(self, bytes, total):
        fraction = self.search_entry.get_progress_fraction() + \
                   (float(bytes) / float(total))
        self.search_entry.set_progress_fraction(fraction)
    
    def back_button_clicked(self, widget):
        self.search_screen.display_results()
        widget.set_sensitive(False)
        self.forecast_button.set_sensitive(False)
        
        self.screen = self.search_screen
        self.set_canvas(self.screen)

    def forecast_button_clicked(self, widget):
        self.forecast_screen.get_daily_forecast()
        widget.set_sensitive(False)
        self.back_button.set_sensitive(True)
        
        self.screen = self.forecast_screen
    
    def show_refresh_button(self):
        self.search_entry.set_icon_from_name(iconentry.ICON_ENTRY_SECONDARY, 
                                            'refresh')
    
    def refresh(self, entry, icon_pos, button):
        self.set_focus(None)
        screen = self.get_canvas()
        screen.refresh()
    
    def temp_scale_combo_toggled(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            scale = model[tree_iter][0]
            self.temp_scale = self.temp_scales[scale]
            
            self.screen.display_results()
    
    def convert(self, kelvin):
        if self.temp_scale == self.temp_scales['Celcius']:
            temp = kelvin - 273.15
        elif self.temp_scale == self.temp_scales['Farenheit']:
            temp = (kelvin * Fraction(9,5)) - 459.67
        else:
            temp = kelvin
        return round(temp, 1)
    
    def select_city(self, city):
        self.selected_city = city
        self.forecast_button.set_sensitive(True)
