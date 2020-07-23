""" Copyright (c) 2015, Swedish Institute of Computer Science
  All rights reserved.
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
  * Neither the name of The Swedish Institute of Computer Science nor the
    names of its contributors may be used to endorse or promote products
    derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE SWEDISH INSTITUTE OF COMPUTER SCIENCE BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Authors: ljjm@sics.se
Testers:
"""

import sys
import json
import hashlib
import traceback
import requests
from pprint import pformat

import cheesepi
from . import dao

logger = cheesepi.config.get_logger(__name__)

try:
    from influxdb import InfluxDBClient
    from influxdb.exceptions import InfluxDBClientError
except AttributeError:
    msg = "Problem importing Python InfluxDB module!\n"
    msg += "Either due to this computer not having a timezone set.\n"
    msg += "Use `raspi-config` > Internationalisation Options to set one.\n"
    msg += "Alternatively, install 'pandas' through pip, rather than apt."
    logger.error(msg)
    sys.exit(1)

host = "localhost"
port = 8086
username = "root"
password = "root"
database = "cheesepi"

class DAO_influx(dao.DAO):
    def __init__(self):
        super().__init__()
        logger.info("Connecting to influx db=%s as user=%s", database, username)
        self.conn = InfluxDBClient(host, port, username, password, database)
        self.make_database(database)

    def make_database(self, name):
        try:
            logger.info("Ensuring database exists")
            self.conn.create_database(name)
        except requests.exceptions.ConnectionError as exception:
            msg = "Error: Connection to Influx database failed! Ensure InfluxDB is running. " + \
                  str(exception)
            print(msg)
            logger.error(msg)
            sys.exit(1)

    def dump(self, since=-1):
        try:
            series = self.conn.get_list_series()
        except requests.exceptions.ConnectionError as exception:
            msg = "Problem connecting to InfluxDB when listing series: " + str(exception)
            logger.error(msg)
            logger.exception(exception)
            sys.exit(1)

        # maybe prune series?
        dumped_db = {}
        for ser in series:
            series_name = ser['name']
            logger.info(series_name)
            query = 'select * from {} where time > {} limit 5;'.format(series_name, 0*1000)
            dumped_series = self.conn.query(query)
            logger.info(dumped_series.raw['results'])
            dumped_db[series_name] = json.dumps(dumped_series.raw['results'])
        return dumped_db

    def format09(self, table, dic):
        return [{"measurement": table,
                 "database": "cheesepi",
                 "fields": dic,
                 "tags": {"source": "dao"}}]

    def format08(self, table, dic):
        for key in dic.keys():
            dic[key] = dic[key]
        #json_dic = [{"name":table, "columns":dic.keys(), "points":[dic.values()]}]
        #json_str = '[{"name":"{}", "columns":{}, "points":[{}]}]'.format(table,json.dumps(dic.keys()),json.dumps(dic.values()))
        json_str = '[{"measurement":"{}", "fields":{}, '.format(table, "")
        #json_str = '[{"name":"ping", "columns":["test"], "points":["value"]}]'
        return json_str

    # Operator interactions
    def write_op(self, op_type, dic, binary=None):
        if not self.validate_op(op_type):
            logger.warning("Operation of type {} not valid: ".format(op_type) + str(dic))
            return
        #if binary!=None:
        #     # save binary, check its not too big
        #     dic['binary'] = bson.Binary(binary)
        config = cheesepi.config.get_config()
        dic['version'] = config['version']
        to_hash = config['secret'] + str(dic)
        dic['sign'] = hashlib.md5(to_hash.encode("utf-8")).hexdigest()

        points = self.format09(op_type, dic)
        logger.debug(points)
        logger.info("Saving {} Op:\n{}".format(op_type, pformat(points)))
        result = None
        try:
            result = self.conn.write_points(points)
        except InfluxDBClientError as exception:
            if exception.code == 204: # success!
                return True
            if exception.code == 404:
                msg = "Database client error, has the database been initialised?"
                print(msg)
                logger.error(msg)
                self.make_database(databse)
                return None
            traceback.print_exc()
        except ConnectionError as exception:
            logger.error("Database connection error, is the database server running?")
            return None
        except Exception as exception:
            msg = "Database Influx " + op_type + " Op write failed! " + str(exception)
            logger.error(msg)
            logger.exception(exception)
            return None
        return result

    def read_op(self, op_type, timestamp=0, limit=100):
        op = self.conn.query('select * from '+op_type+' limit 1;')
        return op

    ## User level interactions
    # Note that assignments are not deleted, but the most recent assignemtn
    # is always returned
    def read_user_attribute(self, attribute):
        try:
            result = self.conn.query('select {} from user limit 1;'.format(attribute))
            if result == []:
                return -1
            column_index = result[0]['columns'].index(attribute)
            value = result[0]['points'][0][column_index]
        except InfluxDBClientError:
            #msg = "Problem connecting to InfluxDB: "+str(e)
            #logger.error(msg)
            return -1
        except Exception as exception:
            msg = "Problem connecting to InfluxDB: " + str(exception)
            logger.error(msg)
            logger.exception(exception)
            sys.exit(1)
        return value

    def write_user_attribute(self, attribute, value):
        # check we dont already exist
        try:
            logger.info("Saving user attribute: {} to {} ".format(attribute, value))
            #json = self.to_json("user", {attribute:value})
            json = self.toFormat("user", {attribute:value})
            logger.debug(json)
            return self.conn.write_points(json)
        except Exception as exception:
            msg = "Problem connecting to InfluxDB: " + str(exception)
            logger.error(msg)
            logger.exception(exception)
            sys.exit(1)
