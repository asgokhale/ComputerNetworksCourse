# Sample code for CS4283-5283
# Vanderbilt University
# Instructor: Aniruddha Gokhale
# Created: Fall 2022
# 
# Code taken from ZeroMQ's sample code for the HelloWorld
# program, but modified to use REQ-REP sockets to showcase
# TCP. But the one change we are doing here is to mimic oneway
# i.e., on the sender side, we are forced to receive a null
# response from the responder.
#
# Plus, we added other decorations like comments, print statements,
# argument parsing, etc.
#
# We should be able to do actual oneway using the RADIO-DISH but
# it is in draft stage and does not work properly.
#
# Note: my default indentation is now set to 2 (in other snippets, it
# used to be 4)

# import the needed packages
import sys    # for system exception
import time   # for sleep
import argparse # for argument parsing
import zmq    # this package must be imported for ZMQ to work

##################################
# Driver program
##################################
def driver (args):
  try:
    # every ZMQ session requires a context
    print ("Obtain the ZMQ context")
    context = zmq.Context ()   # returns a singleton object
  except zmq.ZMQError as err:
    print ("ZeroMQ Error obtaining context: {}".format (err))
    return
  except:
    print ("Some exception occurred getting context {}".format (sys.exc_info()[0]))
    return

  try:
    # The socket concept in ZMQ is far more advanced than the traditional socket in
    # networking. Each socket we obtain from the context object must be of a certain
    # type. For TCP, we will use the REQ socket type (many other pairs are supported)
    # and this is to be used on the client side.
    socket = context.socket (zmq.REQ)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error obtaining REQ socket: {}".format (err))
    return
  except:
    print ("Some exception occurred getting REQ socket {}".format (sys.exc_info()[0]))
    return

  try:
    # as in a traditional socket, tell the system what IP addr and port are we
    # going to connect to. Here, we are using TCP sockets.
    connect_string = "tcp://" + args.addr + ":" + str (args.port)
    print ("TCP client will be connecting to {}".format (connect_string))
    socket.connect (connect_string)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error connecting to server: {}".format (err))
    socket.close ()
    return
  except:
    print ("Some exception occurred connecting REQ socket {}".format (sys.exc_info()[0]))
    socket.close ()
    return

  # since we are a client, we actively send something to the server
  print ("client sending Hello messages for specified num of iterations")
  for i in range (args.iters):
    try:
      #  Wait for next request from client
      print ("Send a HelloWorld")
      socket.send (b"HelloWorld")
    except zmq.ZMQError as err:
      print ("ZeroMQ Error sending: {}".format (err))
      socket.close ()
      return
    except:
      print ("Some exception occurred receiving/sending {}".format (sys.exc_info()[0]))
      socket.close ()
      return

    try:
      #  Here we wait for the null response
      print ("Expecting a null response")
      socket.recv ()  # no need to even receive it in any buffer
    except zmq.ZMQError as err:
      print ("ZeroMQ Error receiving: {}".format (err))
      socket.close ()
      return
    except:
      print ("Some exception occurred receiving/sending {}".format (sys.exc_info()[0]))
      socket.close ()
      return

##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
  # parse the command line
  parser = argparse.ArgumentParser ()

  # add optional arguments
  parser.add_argument ("-a", "--addr", default="127.0.0.1", help="IP Address to connect to (default: localhost i.e., 127.0.0.1)")
  parser.add_argument ("-i", "--iters", type=int, default=10, help="Number of iterations (default: 10")
  parser.add_argument ("-p", "--port", type=int, default=5555, help="Port that server is listening on (default: 5555)")
  args = parser.parse_args ()

  return args
    
#------------------------------------------
# main function
def main ():
  """ Main program """

  print("Demo program for TCP Client with ZeroMQ")

  # first parse the command line args
  parsed_args = parseCmdLineArgs ()
    
  # start the driver code
  driver (parsed_args)

#----------------------------------------------
if __name__ == '__main__':
  # here we just print the version numbers
  print("Current libzmq version is %s" % zmq.zmq_version())
  print("Current pyzmq version is %s" % zmq.pyzmq_version())

  main ()
