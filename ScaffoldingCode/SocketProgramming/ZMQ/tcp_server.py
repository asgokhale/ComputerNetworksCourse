# Sample code for CS4283-5283
# Vanderbilt University
# Instructor: Aniruddha Gokhale
# Created: Fall 2022
# 
# Code taken from ZeroMQ's sample code for the HelloWorld
# program, but modified to use REQ-REP sockets to showcase
# TCP. Plus, added other decorations like comments, print statements,
# argument parsing, etc.
#
# ZMQ is also offering a new CLIENT-SERVER pair of ZMQ sockets but
# these are still in draft form and are not properly supported. If you
# want to try, just replace REP by SERVER here (and correspondingly, in
# the tcp_client.py, replace REQ by CLIENT)
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
    # type. For TCP, we will use REP for server side (many other pairs are supported
    # in ZMQ for tcp.
    print ("Obtain the REP type socket")
    socket = context.socket (zmq.REP)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error obtaining REP socket: {}".format (err))
    return
  except:
    print ("Some exception occurred getting REP socket {}".format (sys.exc_info()[0]))
    return

  try:
    # as in a traditional socket, tell the system what port are we going to listen on
    # Moreover, tell it which protocol we are going to use, and which network
    # interface we are going to listen for incoming requests. This is TCP.
    bind_string = "tcp://" + args.intf + ":" + str (args.port)
    print ("TCP server will be binding on {}".format (bind_string))
    socket.bind (bind_string)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error binding REP socket: {}".format (err))
    socket.close ()
    return
  except:
    print ("Some exception occurred binding REP socket {}".format (sys.exc_info()[0]))
    socket.close ()
    return

  # since we are a server, we service incoming clients forever
  print ("Server now waiting to receive something")
  while True:
    try:
      #  Wait for next request from client
      message = socket.recv()
      print("Received request: %s" % message)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error receiving: {}".format (err))
      socket.close ()
      return
    except:
      print ("Some exception occurred receiving/sending {}".format (sys.exc_info()[0]))
      socket.close ()
      return


    #  Do some 'work'. In this case we just sleep.
    time.sleep (1)

    try:
      #  Send reply back to client
      print ("Send dummy reply")
      socket.send (b"ACK")
    except zmq.ZMQError as err:
      print ("ZeroMQ Error sending: {}".format (err))
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
  parser.add_argument ("-i", "--intf", default="*", help="Interface to bind to (default: *)")
  parser.add_argument ("-p", "--port", type=int, default=5555, help="Port to bind to (default: 5555)")
  args = parser.parse_args ()

  return args
    
#------------------------------------------
# main function
def main ():
  """ Main program """

  print("Demo program for TCP Server with ZeroMQ")

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
