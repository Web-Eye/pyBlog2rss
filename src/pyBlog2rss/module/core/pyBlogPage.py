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
from logging import exception

import requests
from bs4 import BeautifulSoup


class pyBlogPage(object):
    """description of class"""

    def __init__(self, url):

        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        self.__url = url
        page = requests.get(url, headers=headers)
        self._content = BeautifulSoup(page.content, 'lxml')

    @staticmethod
    def __extract_link(e):
        link = e.find('a')
        if link is not None and link.get('href') is not None:
            return link['href']

    @staticmethod
    def _get_rss_id(content):
        element = content.find('div', class_='content clear')
        if element is not None:
            child = element.findChild()
            if child is not None and child.get('id') is not None:
                return child.get('id')

    @staticmethod
    def _get_title(content):
        element = content.find('h1', class_='title_h')
        if element is not None:
            return element.getText()

    @staticmethod
    def _get_tag(content):
        parent = content.find('div', class_='date')
        if parent is not None:
            elements = parent.findAll('a')
            if elements is not None and len(elements) > 1:
                return elements[-1].getText()

    @staticmethod
    def _removeTag(content, name, class_):
        element = content.find(name, class_=class_)
        if element is not None:
            element.decompose()

        return content

    def _get_keywords(self, default):
        e = self._content.find('meta', attrs={"name": "keywords"})
        if e is not None:
            if e.get('content') is not None:
                default = e.get('content')

        return default

    def _getPageTitle(self, default):
        e = self._content.find('title')
        if e is not None:
            default = e.getText()

        return default


    def get_entries(self):

        retValue = []
        elements = self._content.findAll('div', id='shortstory')
        if elements is not None:
            for e in elements:
                link = self.__extract_link(e)
                if link is not None:
                    retValue.append(link)
                        
        return retValue

    def parse_entry(self, feed):
        element = self._content.find('div', id='shortstory')
        if element is not None:

            feed.x_rss_url = self.__url
            feed.x_rss_id = self._get_rss_id(element)
            feed.subject = self._get_title(element)
            feed.x_rss_tags = self._get_tag(element)
            if feed.x_rss_tags is None or feed.x_rss_tags == 'Random':
                feed.x_rss_tags = self._get_keywords(feed.x_rss_tags)

            element = self._removeTag(element, 'div', 'date')
            element = self._removeTag(element, 'div', 'detail clear')
            element = self._removeTag(element, 'div', 'rating')

            soap = BeautifulSoup(str(element), 'lxml')
            tag = soap.new_tag('a', href=feed.x_rss_url)
            tag.string = self._getPageTitle(feed.subject)
            soap.append(tag)
            feed.contents = str(soap)


    def get_next_page_url(self):
        e = self._content.find('div', class_='pagess')
        if e is not None:
            pages = e.findAll('a')
            if pages is not None and len(pages) > 0:
              return pages[-1].get('href')
