# openweathermap.py
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

from gettext import gettext as _

class City(object):
    def __init__(self, info):
        
        self.clouds = get_value(info['clouds'], 'all')
        self.name = get_value(info, 'name')
        self.url = get_value(info, 'url')
        self.country = get_value(info['sys'], 'country')
        self.icon = get_value(info['weather'][0], 'icon')
        self.weather_code = get_value(info['weather'][0], 'id')
        self.weather = condition_codes[self.weather_code]
        self.date = get_value(info, 'dt')
        self.pressure = get_value(info['main'], 'pressure')
        self.temp = get_value(info['main'], 'temp')
        self.temp_max = get_value(info['main'], 'temp_max')
        self.temp_min = get_value(info['main'], 'temp_min')
        self.id = get_value(info, 'id')
        self.humidity = get_value(info['main'], 'humidity')
        self.wind_speed = get_value(info['wind'], 'speed')
        
        self.forecast_daily = []
        self.forecast_hourly = []
    
    def load_forecast_daily(self, dict):
        self.forecast_daily = []
        for key in dict:
            self.forecast_daily.append({
                'clouds' : get_value(key, 'clouds'),
                'icon' : get_value(key['weather'][0], 'icon'),
                'weather_code' : get_value(key['weather'][0], 'id'),
                'weather' : condition_codes[get_value(key['weather'][0], 'id')],
                'date' : get_value(key, 'dt'),
                'temp_day' : get_value(key['temp'], 'day'),
                'temp_night' : get_value(key['temp'], 'night'),
                'wind_speed' : get_value(key, 'speed'),
                'pressure' : get_value(key, 'pressure'),
                'humidity' : get_value(key, 'humidity')})

    def load_forecast_hourly(self, dict):
        self.forecast_hourly = []
        for key in dict:
            self.forecast_hourly.append({
                'clouds' : get_value(key['clouds'], 'all'),
                'icon' : get_value(key['weather'][0], 'icon'),
                'weather_code' : get_value(key['weather'][0], 'id'),
                'weather' : condition_codes[get_value(key['weather'][0], 'id')],
                'date' : get_value(key, 'dt'),
                'temp' : get_value(key['main'], 'temp'),
                'temp_max' : get_value(key['main'], 'temp_max'),
                'temp_min' : get_value(key['main'], 'temp_min'),
                'wind_speed' : get_value(key['wind'], 'speed'),
                'wind_deg' : get_value(key['wind'], 'deg'),
                'pressure' : get_value(key['main'], 'pressure'),
                'humidity' : get_value(key['main'], 'humidity')})

def get_value(dict, key):
        if key in dict:
            value = dict[key]
            if type(value) == unicode:
                return value.encode('utf-8')
            return value
        else:
            return None

condition_codes = {
    200 : _('thunderstorm with light rain'),
    201 : _('thunderstorm with rain'),
    202 : _('thunderstorm with heavy rain'),
    210 : _('light thunderstorm'),
    211 : _('thunderstorm'),
    212 : _('heavy thunderstorm'),
    221 : _('ragged thunderstorm'),
    230 : _('thunderstorm with light drizzle'),
    231 : _('thunderstorm with drizzle'),
    232 : _('thunderstorm with heavy drizzle'),
    300 : _('light intensity drizzle'),
    301 : _('drizzle'),
    302 : _('heavy intensity drizzle'),
    310 : _('light intensity drizzle rain'),
    311 : _('drizzle rain'),
    312 : _('heavy intensity drizzle rain'),
    321 : _('shower drizzle'),
    500 : _('light rain'),
    501 : _('moderate rain'),
    502 : _('heavy intensity rain'),
    503 : _('very heavy rain'),
    504 : _('extreme rain'),
    511 : _('freezing rain'),
    520 : _('light intensity shower rain'),
    521 : _('shower rain'),
    522 : _('heavy intensity shower rain'),
    600 : _('light snow'),
    601 : _('snow'),
    602 : _('heavy snow'),
    611 : _('sleet'),
    621 : _('shower snow'),
    701 : _('mist'),
    711 : _('smoke'),
    721 : _('haze'),
    731 : _('sand/dust whirls'),
    741 : _('fog'),
    761 : _('dust'),
    800 : _('sky is clear'),
    801 : _('few clouds'),
    802 : _('scattered clouds'),
    803 : _('broken clouds'),
    804 : _('overcast clouds'),
    900 : _('tornado'),
    901 : _('tropical storm'),
    902 : _('hurricane'),
    903 : _('cold'),
    904 : _('hot'),
    905 : _('windy'),
    906 : _('hail')}