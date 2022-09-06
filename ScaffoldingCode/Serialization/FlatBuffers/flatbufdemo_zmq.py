#  Author: Aniruddha Gokhale
#  Created: Fall 2021
#  Modified: Fall 2022 (for Computer Networking course)
#
#  Purpose: demonstrate serialization of a user-defined data structure using
#  FlatBuffers combined with ZeroMQ's REQ-REP sample code. Note that here we
#  are more interested in how a serialized packet gets sent over the network
#  and retrieved. To that end, we really don't care even if the client and
#  server were both on the same machine or remote to each other. Thus,
#  to simplify coding, we have mixed both the client and server in the same
#  code so that they run on the same machine. Hence, we term this as a Peer
#  which can don both roles.  When writing code for distributed client and
#  server, just separate the two pieces.
#
#  Here our custom message format comprises a sequence number, a timestamp, a name,
#  and a data buffer of several uint32 numbers (whose value is not relevant to us) 

# The different packages we need in this Python driver code
import os
import sys
import time  # needed for timing measurements and sleep

import random  # random number generator
import argparse  # argument parser

import zmq   # for ZeroMQ

## the following are our files
from custom_msg import CustomMessage  # our custom message in native format
import serialize as sz  # this is from the file serialize.py in the same directory

##################################
#  The Peer class
##################################
class Peer ():
  def __init__ (self):
    self.req = None  # represents the REQ socket
    self.rep = None  # represents the REP socket

  def configure (self, port):
    try:
      # every ZMQ session requires a context
      print ("Obtain the ZMQ context")
      context = zmq.Context ()   # returns a singleton object
    except zmq.ZMQError as err:
      print ("ZeroMQ Error obtaining context: {}".format (err))
      raise
    except:
      print ("Some exception occurred getting context {}".format (sys.exc_info()[0]))
      raise

    try:
      # The socket concept in ZMQ is far more advanced than the traditional socket in
      # networking. Each socket we obtain from the context object must be of a certain
      # type. For TCP, we will use REP for server side (many other pairs are supported
      # in ZMQ for tcp.
      print ("Obtain the REP type socket")
      self.rep = context.socket (zmq.REP)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error obtaining REP socket: {}".format (err))
      raise
    except:
      print ("Some exception occurred getting REP socket {}".format (sys.exc_info()[0]))
      raise

    try:
      # as in a traditional socket, tell the system what port are we going to listen on
      # Moreover, tell it which protocol we are going to use, and which network
      # interface we are going to listen for incoming requests. This is TCP.
      bind_string = "tcp://*:" + str (port)
      print ("TCP server will be binding on {}".format (bind_string))
      self.rep.bind (bind_string)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error binding REP socket: {}".format (err))
      self.rep.close ()
      raise
    except:
      print ("Some exception occurred binding REP socket {}".format (sys.exc_info()[0]))
      self.rep.close ()
      raise

    try:
      # The socket concept in ZMQ is far more advanced than the traditional socket in
      # networking. Each socket we obtain from the context object must be of a certain
      # type. For TCP, we will use REQ for client side (many other pairs are supported
      # in ZMQ for tcp.
      print ("Obtain the REQ type socket")
      self.req = context.socket (zmq.REQ)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error obtaining REQ socket: {}".format (err))
      raise
    except:
      print ("Some exception occurred getting REQ socket {}".format (sys.exc_info()[0]))
      raise

    try:
      # as in a traditional socket, tell the system where we are going to connect
      # to.  In this code, we assume server is on localhost but port is configurable.
      connect_string = "tcp://localhost:" + str (port)
      print ("TCP client will be connecting to {}".format (connect_string))
      self.req.connect (connect_string)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error connecting REQ socket: {}".format (err))
      self.rep.close ()
      raise
    except:
      print ("Some exception occurred connecting REQ socket {}".format (sys.exc_info()[0]))
      self.rep.close ()
      raise

  # clean up
  def cleanup (self):
    # cleanup the sockets
    self.req.close ()
    self.rep.close ()

  # Use the ZMQ's send_serialized method to send the custom message
  def send_request (self, cm):
    """ Send serialized request"""
    try:
      # ZMQ supports a send_serialized method which needs the custom message
      # and a callable serialize method. Technically our "serialize" method
      # is a callable and it returns an iterable (i.e., bytearray) but for some
      # reason, is giving a TypeError. On further debugging, it appears that
      # the type needs to be some sort of a list. Thus, we created a wrapper
      # method called serialize_to_frames that simply returns a [] of the
      # serialized buffer. This works.
      print ("ZMQ sending custom message via ZMQ's send_serialized method")
      self.req.send_serialized (cm, sz.serialize_to_frames)
      # So no need to do the following as an alternative that definitely works.
      #buf = sz.serialize (cm)
      #self.req.send (buf)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error serializing request: {}".format (err))
      raise
    except:
      print ("Some exception occurred with send_serialized {}".format (sys.exc_info()[0]))
      raise

        
  # Send the ACK from server to client
  def send_ack (self):
    """ Send ACK"""
    try:
      # just send the dummy ACK.  Note, this is sent by server to client
      print ("ZMQ sending dummy ACK message")
      self.rep.send (b"ACK")
    except zmq.ZMQError as err:
      print ("ZeroMQ Error sending ACK: {}".format (err))
      raise
    except:
      print ("Some exception occurred with send_ack {}".format (sys.exc_info()[0]))
      raise

  # Use the ZMQ's recv_serialized method to send the custom message
  def recv_request (self):
    """ receive serialized request"""
    try:
      # ZMQ supports a recv_serialized method which needs a deserialize method.
      # Technically our "deserialize" method is a callable but it is unclear if
      # it can work with frames. So falling back on traditional recv method.
      print ("ZMQ receiving serialized custom message")
      # Note, in the following, if copy=False, then what is received is
      # a list of frames and not bytes
      cm = self.rep.recv_serialized (sz.deserialize_from_frames, copy=True)
      #buf = self.rep.recv ()
      #cm = sz.deserialize (buf)
      return cm
    except zmq.ZMQError as err:
      print ("ZeroMQ Error receiving serialized message: {}".format (err))
      raise
    except:
      print ("Some exception occurred with recv_serialized {}".format (sys.exc_info()[0]))
      raise

  # receive the dummy ACK on client side
  def recv_ack (self):
    """ receive dummy ACK"""
    try:
      # receive dummy ack on client side.
      print ("ZMQ receiving dummy ACK")
      #self.rep.recv_serialized (sz.deserialize)
      buf = self.req.recv ()
    except zmq.ZMQError as err:
      print ("ZeroMQ Error receiving dummy ack: {}".format (err))
      raise
    except:
      print ("Some exception occurred with recv_ack {}".format (sys.exc_info()[0]))
      raise

        
        
##################################
#        Driver program
##################################

def driver (name, iters, vec_len, port):

  print ("Driver program: Name = {}, Num Iters = {}, Vector len = {}, Peer port = {}".format (name, iters, vec_len, port))

  # first obtain a peer and initialize it
  print ("Driver program: create and configure a peer object")
  peer = Peer ()
  try:
    peer.configure (port)
  except:
    print ("Some exception occurred")
    return
  
  # now send the serialized custom message for the number of desired iterations
  cm = CustomMessage ()   # create this once and reuse it for send/receive

  for i in range (iters):
        
    # for every iteration, let us fill up our custom message with some info
    cm.seq_num = i # this will be our sequence number
    cm.ts = time.time ()  # current time
    cm.name = name # assigned name
    cm.vec = [random.randint (1, 1000) for j in range (vec_len)]
    print ("-----Iteration: {} contents of message before serializing ----------".format (i))
    cm.dump ()

    # Recall that we are a peer running on the same machine, and because
    # we are using the REQ-REP pattern, there has to be a response
    # from server to client side. Here we send a dummy ACK which does not
    # need any serialization.
    try:
      # now let the peer send the message to its server part
      print ("Peer client sending the serialized message")
      start_time = time.time ()
      peer.send_request (cm)
      end_time = time.time ()
      print ("Serialization took {} secs".format (end_time-start_time))
    except:
      return

    try:
      # now let the peer receive the message at the server end
      print ("Peer client sending the serialized message")
      start_time = time.time ()
      cm = peer.recv_request ()
      end_time = time.time ()
      print ("Deserialization took {} secs".format (end_time-start_time))
      print ("------ contents of message after deserializing ----------")
      cm.dump ()
    except:
      return

    try:
      # now let the peer send the ACK
      print ("Peer server sending ACK")
      peer.send_ack ()
    except:
      return

    try:
      # now let the peer receive the ack
      print ("Peer client receiving the ACK")
      peer.recv_ack ()
    except:
      return

    # sleep a while before we send the next serialization so it is not
    # extremely fast
    time.sleep (0.050)  # 50 msec

  # we are done. Just cleanup the peer before exiting
  peer.cleanup ()
  
##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-i", "--iters", type=int, default=10, help="Number of iterations to run (default: 10)")
    parser.add_argument ("-l", "--veclen", type=int, default=20, help="Length of the vector field (default: 20; contents are irrelevant)")
    parser.add_argument ("-n", "--name", default="FlatBuffer ZMQ Demo", help="Name to include in each message")
    parser.add_argument ("-p", "--port", type=int, default=5555, help="Port where the server part of the peer listens and client side connects to (default: 5555)")
    # parse the args
    args = parser.parse_args ()

    return args
    
#------------------------------------------
# main function
def main ():
  """ Main program """

  print("Demo program for Flatbuffer serialization/deserialization")

  # first parse the command line args
  parsed_args = parseCmdLineArgs ()
    
  # start the driver code
  driver (parsed_args.name, parsed_args.iters, parsed_args.veclen, parsed_args.port)

#----------------------------------------------
if __name__ == '__main__':
    main ()
