#  Author: Aniruddha Gokhale
#  Created: Fall 2023
#
#  Purpose: demonstrate serialization of a user-defined data structure using
#  Protocol Buffers combined with gRPC. Note that here we
#  are more interested in how a serialized packet gets sent over the network
#  and retrieved. To that end, we really don't care even if the client and
#  server were both on the same machine or remote to each other.

# This one implements the client functionality
#

# Note that this code mimics what we did with FlatBufs+ZeroMQ but this time
# we mix Protocol Buffers and gRPC

# The different packages we need in this Python driver code
import os
import sys
import time  # needed for timing measurements and sleep

import random  # random number generator
import argparse  # argument parser

import logging

import grpc   # for gRPC

# import generated packages
import schema_pb2 as spb
import schema_pb2_grpc as spb_grpc

##################################
#        Driver program
##################################

def driver (name, iters, vec_len, port):

  print ("Driver program: Name = {}, Num Iters = {}, Vector len = {}, Peer port = {}".format (name, iters, vec_len, port))

  # first obtain a peer and initialize it
  print ("Driver program: create handle to the client and then run the code")
  try:

    # Use the insecure channel to establish connection with server
    print ("Instantiate insecure channel")
    channel = grpc.insecure_channel ("localhost:" + str (port))

    print ("Obtain a proxy object to the server")
    stub = spb_grpc.DummyServiceStub (channel)

    # now send the serialized custom message for the number of desired iterations
    print ("Allocate the Request object that we will then populate in every iteration")
    req = spb.Request ()

    for i in range (iters):
      # for every iteration, let us fill up our custom message with some info
      req.seq_no = i # this will be our sequence number
      req.ts = time.time ()  # current time
      req.name = name # assigned name
      req.data[:] = [random.randint (1, 1000) for j in range (vec_len)]
      print ("-----Iteration: {} contents of message before sending\n{} ----------".format (i, req))

      # now let the client send the message to its server part
      print ("Peer client sending the serialized message")
      start_time = time.time ()
      resp = stub.method (req)
      end_time = time.time ()
      print ("sending/receiving took {} secs".format (end_time-start_time))

      # sleep a while before we send the next serialization so it is not
      # extremely fast
      time.sleep (0.050)  # 50 msec

  except:
    return

  
##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-i", "--iters", type=int, default=10, help="Number of iterations to run (default: 10)")
    parser.add_argument ("-l", "--veclen", type=int, default=20, help="Length of the vector field (default: 20; contents are irrelevant)")
    parser.add_argument ("-n", "--name", default="ProtoBuf gRPC Demo", help="Name to include in each message")
    parser.add_argument ("-p", "--port", type=int, default=5577, help="Port where the server part of the peer listens and client side connects to (default: 5577)")
    
    # parse the args
    args = parser.parse_args ()

    return args
    
#------------------------------------------
# main function
def main ():
  """ Main program """

  print("Demo program for Protocol Buffers with gRPC serialization/deserialization")

  # first parse the command line args
  parsed_args = parseCmdLineArgs ()
    
  # start the driver code
  driver (parsed_args.name, parsed_args.iters, parsed_args.veclen, parsed_args.port)

#----------------------------------------------
if __name__ == '__main__':
    main ()
