#  Author: Aniruddha Gokhale
#  Created: Fall 2022
#  (based on code developed for Distributed Systems course in Fall 2019)
#
#  Purpose: demonstrate serialization of user-defined packet structure
#  using JSON
#
#  Here our packet or message format comprises a sequence number, a timestamp,
#  and a data buffer of several uint32 numbers (whose value is not relevant to us)

import os
import sys

import json # JSON package

from custom_msg import CustomMessage  # our custom message in native format

# This is the method we will invoke from our driver program to convert a data structure
# in native format to JSON
def serialize (cm):

  # create a JSON representation from the original data structure
  json_buf = {
    "seq_num": cm.seq_num,
    "timestamp": cm.ts,
    "name": cm.name,
    "vector": cm.vec
    }
  
  # return the underlying jsonified buffer
  return json.dumps (json_buf)

# deserialize the incoming serialized structure into native data type
def deserialize (buf):

  # get the json representation from the incoming buffer
  json_buf = json.loads (buf)

  # now retrieve the native data structure out of it.
  cm = CustomMessage ()
  cm.seq_num = json_buf["seq_num"]
  cm.ts = json_buf["timestamp"]
  cm.name = json_buf["name"]
  cm.vec = json_buf["vector"]

  return cm
    
    
