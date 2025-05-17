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


from ..postgresUtils import *
from .pyBlogPage import pyBlogPage
import time
from ..data_layer.DL_feed import DL_feed
from ..mailUtils import *


class pyBlogCore(object):
    """description of class"""

    def __init__(self, connectionstring):

        self.__project_id = 0
        self.__url = None
        self.__email_recipient = None
        self.__default_page_count = None
        self.__hoster_whitelist = None
        self.__hoster_blacklist = None

        self.__conn = database_connect(connectionstring)
        if self.__conn is None:

            raise Exception("could not connect to internal database")

    def __del__(self):

        if self.__conn is not None:
            self.__conn.close()

    def __insert_feed(self, feed):
        query = 'INSERT INTO wrss_feed(project_id, x_rss_id, x_rss_url, x_rss_tags, subject, contents, passed) ' \
                'VALUES (%s, %s, %s, %s, %s, %s, %s);'

        return execute_non_query(self.__conn, query,
                                 (self.__project_id, feed.x_rss_id, feed.x_rss_url, feed.x_rss_tags, feed.subject,
                                  feed.contents, 'false'))

    def __feed_exists(self, x_rss_id):
        return execute_scalar(self.__conn, "SELECT COUNT(*) FROM wrss_feed WHERE x_rss_id = %s", (x_rss_id,)) != 0
     
    def __feed_blacklisted(self, x_rss_tag):
        query = "SELECT Count(*) FROM wrss_blacklist WHERE %s LIKE '%%' || matchcode || '%%'"

        return execute_scalar(self.__conn, query, (x_rss_tag, )) != 0

    def __process_mails(self, project_id):
        query = "SELECT feed_id, project_id, x_rss_id, x_rss_url, x_rss_tags, subject, contents FROM wrss_feed " \
                "WHERE project_id = " + str(project_id) + " AND NOT passed ORDER BY x_rss_id"

        cur = open_cursor(self.__conn, query,  psycopg2.extras.DictCursor)
        if cur is not None:

            while True:

                row = cur.fetchone()

                if row is None:
                    break
        
                send_mail('web2rss@localhost', self.__email_recipient, row['subject'], 'web2rss', row['x_rss_id'],
                          row['x_rss_url'], row['x_rss_tags'], self.__url, row['contents'])
                execute_non_query(self.__conn, "UPDATE wrss_feed SET passed = True WHERE feed_id = %s",
                                  (row['feed_id'],))
                
                time.sleep(1)

            cur.close()


    def start(self):

        if self.__conn is not None:
            query = "   SELECT project_id, web_page, email_recipient, default_page_count, hoster_whitelist," \
                    "          hoster_blacklist, activated FROM wrss_project" \
                    "   WHERE activated;"

            cur = open_cursor(self.__conn, query, psycopg2.extras.DictCursor)
            if cur is not None:
                 
                while True:

                    row = cur.fetchone()

                    if row is None:
                        break

                    self.__project_id = row['project_id']
                    self.__url = row['web_page']
                    self.__email_recipient = row['email_recipient']
                    self.__default_page_count = row['default_page_count']
                    self.__hoster_whitelist = row['hoster_whitelist']
                    self.__hoster_blacklist = row['hoster_blacklist']

                    url = self.__url
                    page_count = 0
                    deathCount = 0
               
                    while url is not None:

                        page_count = page_count + 1
                        if page_count > self.__default_page_count:
                            break

                        page = pyBlogPage(url)
                        entries = page.get_entries()
                        exists = False

                        if entries is not None:

                            for sub_url in entries:

                                sub_page = pyBlogPage(sub_url)
                                feed = DL_feed()
                                feed.x_rss_feed = self.__url
                                sub_page.parse_entry(feed, self.__hoster_whitelist, self.__hoster_blacklist)
                                valid = feed.isValid() and not self.__feed_blacklisted(feed.x_rss_tags)
                                if valid:

                                    exists = self.__feed_exists(feed.x_rss_id)
                                    if not exists:
                                        deathCount = 0
                                        self.__insert_feed(feed)
                                    else:
                                        deathCount += 1

                        if deathCount > 9:
                            break

                        url = page.get_next_page_url()

                    self.__process_mails(self.__project_id)

                cur.close()

               