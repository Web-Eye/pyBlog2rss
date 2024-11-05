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

from module.common.PIDhandler import PIDhandler
from module.core.pyBlogCore import pyBlogCore

if __name__ == "__main__":

    h = PIDhandler("pyBlog2rss.pid")
    h.checkPID()
    
    try:

        dbname = ''
        username = ''
        password = ''
        host = ''

        core = pyBlogCore(f'dbname=\'{dbname}\' user=\'{username}\' password=\'{password}\' host=\'{host}\'')
        core.start()

        del core

    except Exception as e:
        print(e)

    h.unlinkPID()
