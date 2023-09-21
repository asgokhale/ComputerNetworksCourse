#  Author: Aniruddha Gokhale
#  Created: Fall 2023
#
#  Purpose: demonstrate serialization of a user-defined data structure using
#  Protocol Buffers combined with gRPC. Note that here we
#  are more interested in how a serialized packet gets sent over the network
#  and retrieved. To that end, we really don't care even if the client and
#  server were both on the same machine or remote to each other. Thus,
#  to simplify coding, we have mixed both the client and server in the same
#  code so that they run on the same machine. Hence, we term this as a Peer
#  which can don both roles.  When writing code for distributed client and
#  server, just separate the two pieces.
#

# Note that this code mimics what we did with FlatBufs+ZeroMQ but this time
# we mix Protocol Buffers and gRPC

# The different packages we need in this Python driver code
import os
import sys
import time  # needed for timing measurements and sleep

import random  # random number generator
import argparse  # argument parser

from concurrent import futures   # needed for thread pool
import logging

import grpc   # for gRPC
# import generated packages
import schema_pb2 as spb
import schema_pb2_grpc as spb_grpc

##################################
#  The Service implementation class
##################################
class ServiceHandler (spb_grpc.DummyServiceServicer):
  
  # Implement the method message that gets called on us via an upcall
  # Note, we have to use the same name for the method because it must be an
  # overridden method
  def method (self, request, context):
    """ Handle request message """
    try:
      # here, let us just print what we got.
      print ("Received request - seq no: {}, timestamp: {}, name: {}, data: {}".format (request.seq_no, request.ts, request.name, request.data))

      # Now send response
      resp = spb.Response ()  # allocate the response object. Note it is empty
      return resp   # note that this is what is supposed to be returned
    except:
      print ("Some exception occurred handling method {}".format (sys.exc_info()[0]))
      raise

##################################
#        Driver program
##################################

def driver (port):

  print ("Driver program: Port = {}".format (port))

  # run the program
  print ("Driver program: create and run the server")

  try:
  
    # Create a server handle
    print ("Create a server handle")
    server = grpc.server (futures.ThreadPoolExecutor (max_workers=10))

    # Now create our message handler object
    print ("Instantiate our service handler")
    handler = ServiceHandler ()

    # Make the binding between the stub and the handler
    print ("Make the connection between our handler class and server")
    spb_grpc.add_DummyServiceServicer_to_server(handler, server)

    print ("Add port to our server")
    server.add_insecure_port("[::]:" + str (port))

    print ("Start the server")
    server.start()

    print("Server started, listening on {}".format (port))
    server.wait_for_termination()

  except:
    print ("Some exception occurred {}".format (sys.exc_info()[0]))
    return
  
  
##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
    # parse the command line
    parser = argparse.ArgumentParser ()

    # add optional arguments
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
  driver (parsed_args.port)

#----------------------------------------------
if __name__ == '__main__':
    main ()
