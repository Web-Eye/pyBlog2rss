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


    # @staticmethod
    # def __extract_links(e):
    #     href = html.fromstring(tostring(e))
    #     return href.xpath("//a")
    #
    # @staticmethod
    # def __extract_tag(e, path, item):
    #     href = html.fromstring(tostring(e))
    #     p = href.xpath(path)
    #     if p is not None and item in p:
    #         return p[item]
    #
    # @staticmethod
    # def __extract_id(e, path):
    #     p = e.xpath(path)
    #     if p is not None and len(p) > 0:
    #         element = p[0]
    #         if element is not None:
    #             element = element.getchildren()
    #             if element is not None and len(element) > 0:
    #                 element = element[0]
    #                 return element.get('id')
    #
    # def __extract_keywords(self):
    #     p = self.__page_tree.xpath('//meta[@name="keywords"]')
    #     if p is not None and len(p) > 0:
    #         retValue = p[0].get("content")
    #         return retValue
    #
    # @staticmethod
    # def __remove_element(e, path):
    #     tree = html.fromstring(tostring(e))
    #
    #     for bad in tree.xpath(path):
    #         bad.getparent().remove(bad)
    #
    #     return tree
    #
    # def __get_tag(self):
    #
    #     return html.fromstring('<a href="' + self.__url + '">' + self.__page_tree.xpath("//title")[0].text + '</a>')

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
            return element.getText

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

        # tag = self.__get_tag()
        # p = self.__page_tree.xpath('//*[@id="shortstory"]')
        # if p is not None and len(p) > 0:
        #     e = p[0]
        #
        #     feed.x_rss_url = self.__url
        #     feed.x_rss_id = self.__extract_id(e, '//div[@class="content clear"]')
        #     feed.subject = self.__extract_tag(e, '//h1[@class="title_h"]', 0).text
        #     feed.x_rss_tags = self.__extract_tag(e, '//a', 1).text
        #     if feed.x_rss_tags is None or feed.x_rss_tags == 'Random':
        #         feed.x_rss_tags = self.__extract_keywords()
        #
        #     e = self.__remove_element(e, '//div[@class="date"]')
        #     e = self.__remove_element(e, '//div[@class="detail clear"]')
        #     e = self.__remove_element(e, '//div[@class="rating"]')
        #     e.append(tag)
        #
        #     feed.contents = tostring(e)

        element = self._content.find('div', id='shortstory')
        if element is not None:
            feed.x_rss_url = self.__url
            feed.x_rss_id = self._get_rss_id(element)
            feed.subject = self._get_title(element)
            # feed.x_rss_tags = self.__extract_tag(e, '//a', 1).text
            # if feed.x_rss_tags is None or feed.x_rss_tags == 'Random':
            #     feed.x_rss_tags = self.__extract_keywords()
            #
            # e = self.__remove_element(e, '//div[@class="date"]')
            # e = self.__remove_element(e, '//div[@class="detail clear"]')
            # e = self.__remove_element(e, '//div[@class="rating"]')


    # def get_next_page_url(self):
    #     p = self.__page_tree.xpath('//div[@class="pagess"]')
    #     if p is not None and len(p) > 0:
    #         e = p[0]
    #         retValue = e[len(e) - 1].get("href")
    #         return retValue
        