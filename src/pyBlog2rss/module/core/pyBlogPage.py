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
import time
from stem import Signal
from stem.control import Controller
import logging
import traceback
import sys


import requests
import re
from bs4 import BeautifulSoup
import warnings
from bs4.builder import XMLParsedAsHTMLWarning


class pyBlogPage(object):
    """description of class"""

    def __init__(self, url):

        logging.basicConfig(
            filename="/var/log/pyBlog2rss.log",
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )

        warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

        # session = requests.session()
        # session.proxies = {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}
        #
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        # }
        #
        # self.__url = url
        # # page = requests.get(url, headers=headers)
        # page = session.get(url, headers=headers)

        logging.debug(f"pyBlogPage __init__ {url}")
        self.__url = url
        page = self.get_with_fallback(url)
        if page is not None and page.content is not None:
            logging.debug(f"pyBlogPage __init__ get_content successfully")
            self._content = BeautifulSoup(page.content, 'lxml')
            logging.debug(f"pyBlogPage __init__ end....")

    @staticmethod
    def renew_tor_ip():
        logging.debug(f"renew tor ip")

        try:
            with Controller.from_port(port=9051) as c:
                c.authenticate()
                c.signal(Signal.NEWNYM)
                logging.debug("successfully sent signal tor-renew")

        except Exception as e:
            logging.error("Failed to renew Tor IP")
            logging.error(str(e))
            logging.error(traceback.format_exc())

    @staticmethod
    def create_session(use_tor=False):
        logging.debug(f"create session use_tor={use_tor}")
        s = requests.Session()

        if use_tor:
            s.proxies = {
                "http": "socks5h://localhost:9050",
                "https": "socks5h://localhost:9050",
            }

        s.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        })

        return s

    def get_with_fallback(self, url, max_retries = 2, max_tor_retries=2, timeout=10):

        logging.debug(f"get with fallback {url}")
        for attempt in range(1, max_retries + 1):
            try:
                with self.create_session(use_tor=False) as session:
                    r = session.get(url, timeout=(timeout, timeout*3))

                    if r.status_code == 403:
                        raise requests.HTTPError(response=r)

                    r.raise_for_status()
                    return r

            except requests.Timeout:
                logging.debug("timeout, retrying...")
                time.sleep(timeout)

            except requests.ConnectionError:
                logging.debug("connection error, retrying...")
                time.sleep(timeout)

            except requests.HTTPError as e:
                if e.response.status_code == 403:
                    logging.debug("getting HTTPCode 403")
                    break
                raise

        logging.debug("Retry limit reached or getting or getting HTTPCode 403: switching to Tor")
        lastError = None

        for attempt in range(1, max_tor_retries + 1):
            try:
                with self.create_session(use_tor=True) as session:
                    r = session.get(url, timeout=(timeout, timeout*3))

                    if r.status_code == 403:
                        logging.debug("getting HTTPCode 403: renewing IP")
                        self.renew_tor_ip()
                        time.sleep(timeout)
                        continue

                    r.raise_for_status()
                    return r

            except requests.Timeout:
                lastError = requests.Timeout
                logging.debug("timeout, retrying...")
                time.sleep(timeout)

            except requests.ConnectionError:
                lastError = requests.ConnectionError
                logging.debug("connection error, retrying...")
                time.sleep(timeout)

        logging.error("Failed after direct and tor retries")
        if lastError != requests.Timeout:
            raise RuntimeError("Failed after direct and tor retries")

        return None

    @staticmethod
    def __extract_link(e):
        if e is not None:
            link = e.find('a')
            if link is not None and link.get('href') is not None:
                return link['href']

        return None

    @staticmethod
    def _get_rss_id(content):
        if content is not None:
            element = content.find('div', class_='content clear')
            if element is not None:
                child = element.findChild()
                if child is not None and child.get('id') is not None:
                    return child.get('id')

        return None

    @staticmethod
    def _get_title(content):
        if content is not None:
            element = content.find('h1', class_='title_h')
            if element is not None:
                return element.getText()

        return None

    @staticmethod
    def _get_tag(content):
        if content is not None:
            parent = content.find('div', class_='date')
            if parent is not None:
                elements = parent.findAll('a')
                if elements is not None and len(elements) > 1:
                    return elements[-1].getText()

        return None

    @staticmethod
    def _removeTag(content, name, class_):
        if content is not None:
            element = content.find(name, class_=class_)
            if element is not None:
                element.decompose()

        return content

    def _get_keywords(self, default):
        if self._content is not None:
            e = self._content.find('meta', attrs={"name": "keywords"})
            if e is not None:
                if e.get('content') is not None:
                    default = e.get('content')

        return default

    def _getPageTitle(self, default):
        if self._content is not None:
            e = self._content.find('title')
            if e is not None:
                default = e.getText()

        return default


    def get_entries(self):

        retValue = []
        if self._content is not None:
            elements = self._content.findAll('div', id='shortstory')
            if elements is not None:
                for e in elements:
                    link = self.__extract_link(e)
                    if link is not None:
                        retValue.append(link)
                        
        return retValue

    def _isHosterFiltered(self, hoster_whitelist, hoster_blacklist):
        if self._content is not None:
            if (hoster_whitelist and hoster_whitelist != '') or (hoster_blacklist and hoster_blacklist != ''):
                detailBlock = self._content.find('div', id=re.compile('news.*'))
                if detailBlock is not None:
                    test = detailBlock.find()
                    valid = None

                    for t in test:
                        if t.name == 'a' and t.find('img') is None and t.has_attr('href'):
                            h = ''.join(['' if ord(i) < 20 else i for i in t.getText()])
                            if h != '' and t['href'] != '':

                                if valid is None:
                                    valid = True

                                if hoster_whitelist and hoster_whitelist != '':
                                    match = re.match(hoster_whitelist, t['href'])
                                    valid = (not match is None)

                                if valid and hoster_blacklist and hoster_blacklist != '':
                                    match = re.match(hoster_blacklist, t['href'])
                                    valid = (match is None)

                                if valid:
                                    return False

                    return True

        return False

    def parse_entry(self, feed, hoster_whitelist, hoster_blacklist):

        if self._content is not None:

            feed.valid = not self._isHosterFiltered(hoster_whitelist, hoster_blacklist)

            if feed.valid:
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
        if self._content is not None:
            e = self._content.find('div', class_='pagess')
            if e is not None:
                pages = e.findAll('a')
                if pages is not None and len(pages) > 0:
                  return pages[-1].get('href')

        return None


class ForbiddenError(Exception):
    pass

class BlockedError(Exception):
    pass