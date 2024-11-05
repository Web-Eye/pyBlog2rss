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

class DL_feed(object):
    """description of class"""

     # x_rss_id
     # x_rss_url
     # x_rss_tags
     # subject 
     # contents

    def __init__(self):
         
        self.__x_rss_id = None
        self.__x_rss_url = None
        self.__x_rss_tags = None
        self.__subject = None
        self.__contents = None

    @property
    def x_rss_id(self):
        return self.__x_rss_id

    @x_rss_id.setter
    def x_rss_id(self, x_rss_id):
        self.__x_rss_id = x_rss_id

    @property
    def x_rss_url(self):
        return self.__x_rss_url

    @x_rss_url.setter
    def x_rss_url(self, x_rss_url):
        self.__x_rss_url = x_rss_url

    @property
    def x_rss_tags(self):
        return self.__x_rss_tags

    @x_rss_tags.setter
    def x_rss_tags(self, x_rss_tags):
        self.__x_rss_tags = x_rss_tags

    @property
    def subject(self):
        return self.__subject

    @subject.setter
    def subject(self, subject):
        self.__subject = subject

    @property
    def contents(self):
        return self.__contents

    @contents.setter
    def contents(self, contents):
        self.__contents = contents



