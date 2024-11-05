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

import psycopg2
import psycopg2.extras


def database_connect(connectionstring):
    try:
        conn = psycopg2.connect(connectionstring)
    except:
        conn = None

    return conn


def open_cursor(conn, sql, cf=None):
    cur = conn.cursor(cursor_factory=cf)
    try:
        cur.execute(sql)
    except:
        cur = None

    return cur


def execute_non_query(conn, operation, parameters):
    retValue = None
    cur = conn.cursor()
    try:
        retValue = cur.execute(operation, parameters)
        conn.commit()
    except Exception as e:
        print(e)
        cur = None

    return retValue


def execute_scalar(conn, operation, parameters):
    retValue = False
    cur = conn.cursor()

    try:

        cur.execute(operation, parameters)
        row = cur.fetchone()
        retValue = row[0]

    except Exception as e:
        print(e)

    cur.close()

    return retValue
