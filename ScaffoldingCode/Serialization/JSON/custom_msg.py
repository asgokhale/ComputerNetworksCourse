# CS4283/5283: Computer Networks
# Instructor: Aniruddha Gokhale
# Created: Fall 2022
#
# Purpose: Define a native representation of a custom message format
#          that will then undergo serialization/deserialization
#

from typing import List
from dataclasses import dataclass

@dataclass
class CustomMessage:
  """ Our message in native representation"""
  seq_num: int  # a sequence number
  ts: float    # timestamp
  name: str    # some name
  vec: List[int] # some vector of unsigned ints

  def __init__ (self):
    pass
  
  def dump (self):
    print ("Dumping contents of Custom Message")
    print ("  Seq Num: {}".format (self.seq_num))
    print ("  Timestamp: {}".format (self.ts))
    print ("  Name: {}".format (self.name))
    print ("  Vector type = {}".format (type (self.vec)))
    print ("  Vector: {}".format (self.vec))
  
