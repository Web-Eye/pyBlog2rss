# -*- coding: utf-8 -*-
# Copyright 2024 WebEye
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import json
import sys
import os

from module.common.PIDhandler import PIDhandler
from module.core.pyBlogCore import pyBlogCore

def getDefaultConfigFile():
    if sys.platform == "linux" or sys.platform == "linux2":
        return '/etc/pyBlog2rss.config'

    elif sys.platform == "darwin":
        # MAC OS X
        return None

    elif sys.platform == "win32":
        return 'C:\\python\\etc\\pyBlog2rss.config'

    return None

def getConfig():
    _config = {}
    config_file = getDefaultConfigFile()
    if os.path.isfile(config_file):
        with open(config_file) as json_data_file:
            _config = json.load(json_data_file)

    return _config

if __name__ == "__main__":

    h = PIDhandler("pyBlog2rss.pid")
    h.checkPID()
    
    try:

        config = getConfig()

        dbname = config['dbname']
        username =  config['username']
        password = config['password']
        host = config['host']

        core = pyBlogCore(f'dbname=\'{dbname}\' user=\'{username}\' password=\'{password}\' host=\'{host}\'')
        core.start()

        del core

    except Exception as e:
        print(e)

    h.unlinkPID()
