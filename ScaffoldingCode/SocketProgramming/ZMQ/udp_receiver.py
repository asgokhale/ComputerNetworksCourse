# Sample code for CS4283-5283
# Vanderbilt University
# Instructor: Aniruddha Gokhale
# Created: Fall 2022
# 
# Code taken from ZeroMQ's sample code for the HelloWorld
# program, but modified to use RADIO-DISH sockets to showcase
# UDP. Plus, added other decorations like comments, print statements,
# argument parsing, etc.
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
    # type. For UDP, the only socket type supported so far in ZMQ is the RADIO-DISH
    # socket pair, of which DISH is to be used on the receiver side.  Note, that the
    # RADIO DISH is for one to many oneway transfers.
    print ("Obtain the ZMQ DISH socket")
    socket = context.socket (zmq.DISH)
    socket.rcvtimeo = 10000  # some number
  except zmq.ZMQError as err:
    print ("ZeroMQ Error obtaining DISH socket: {}".format (err))
    return
  except:
    print ("Some exception occurred getting DISH socket {}".format (sys.exc_info()[0]))
    return

  try:
    # as in a traditional socket, tell the system what port are we going to listen on
    # Moreover, tell it which protocol we are going to use, and which network
    # interface we are going to listen for incoming requests.  Since we want to use
    # UDP, we use the udp:// prefix.
    bind_string = "udp://" + args.intf + ":" + str (args.port)
    print ("UDP server will be binding on {}".format (bind_string))
    socket.bind (bind_string)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error binding DISH socket: {}".format (err))
    socket.close ()
    return
  except:
    print ("Some exception occurred binding DISH socket {}".format (sys.exc_info()[0]))
    socket.close ()
    return

  try:
    # a DISH socket can join a group
    print ("UDP server joining group {}".format (args.group))
    socket.join (args.group)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error joining group: {}".format (err))
    # There seems to be some crazy behavior where an exception gets
    # thrown while joining but actually it is a success
    if (err.errno != 0):
      socket.close ()
      return
    else:
      pass
  except:
    print ("Some exception occurred joining group {}".format (sys.exc_info()[0]))
    socket.close ()
    return

  # since we are a receiver, we service incoming senders forever
  print ("Receiver now waiting to receive something")
  while True:
    try:
      #  Wait for next request from client
      message = socket.recv (copy=False)
      print ("Received request: %s" % message)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error receiving: {}".format (err))
      socket.close ()
      return
    except zmq.Again:
      print ("ZeroMQ missed a message")
      continue
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
  parser.add_argument ("-g", "--group", default="demo", help="Group to join (default: demo)")
  parser.add_argument ("-i", "--intf", default="*", help="Interface to bind to (default: *)")
  parser.add_argument ("-p", "--port", type=int, default=7777, help="Port to bind to (default: 7777)")
  args = parser.parse_args ()

  return args
    
#------------------------------------------
# main function
def main ():
  """ Main program """

  print("Demo program for UDP Server with ZeroMQ")

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
