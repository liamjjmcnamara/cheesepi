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

import logging
import hashlib

# PyMongo
import pymongo
import gridfs
import bson
from bson.json_util import dumps

import cheesepi as cp
import dao

class DAO_mongo(dao.DAO):
    def __init__(self):
        try: # Get a hold of a MongoDB connection
            self.conn = pymongo.MongoClient('localhost', 27017 )
        except:
            msg = "Error: Connection to Mongo database failed! Ensure MongoDB is running."
            logging.error(msg)
            print msg
            exit(1)
        self.db = self.conn.cheesepi
        self.fs = gridfs.GridFS(self.db)

    def close(self):
        # the following does not close() permenantly, reusing the
        # connection object will reopen it
        self.conn.close()


    # Operator interactions
    def write_op(self, op_type, dic, binary=None):
        if not self.validate_op(op_type,dic):
            return
        collection = self.db[op_type]
        if binary!=None:
            # save binary, check its not too big
            dic['binary'] = bson.Binary(binary)
        config = cp.config.get_config()
        dic['version'] = config['version']
        md5 = hashlib.md5(config['secret']+str(dic)).hexdigest()
        dic['sign']    = md5

        print "Saving %s Operation: %s" % (op_type, dic)
        try:
            id = collection.insert(dic)
        except:
            logging.error("Database PyMongo write failed!")
            exit(1)
        return id


    def read_op(self, op_type, timestamp=0, limit=100):
        rv=""
        if not self.validate_op(op_type):
            return
        collection = self.db[op_type]
        for op in collection.find():
            rv += str(dumps(op))
        return rv


    # user level interactions
    def read_user_attribute(self, attribute):
        return self.db.user.find()


    def write_user_attribute(self, attribute, value):
        print "Setting %s to %s " % (attribute, value)
        where = {'attribute': attribute}
        data  = {'attribute': attribute, 'value': value}
        return self.db.user.update(where, data, {'upsert': True})


    def to_bson(self, i):
        """if not bson, convert to bson"""
        return dumps(i)


