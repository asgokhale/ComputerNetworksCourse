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
  except:
    print ("Some exception occurred getting context {}".format (sys.exc_info()[0]))

  try:
    # The socket concept in ZMQ is far more advanced than the traditional socket in
    # networking. Each socket we obtain from the context object must be of a certain
    # type. For UDP, the only socket type supported so far in ZMQ is the RADIO socket
    # and this is to be used on the sender side.
    print ("Obtain ZMQ RADIO socket")
    socket = context.socket (zmq.RADIO)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error obtaining RADIO socket: {}".format (err))
    return
  except:
    print ("Some exception occurred getting RADIO socket {}".format (sys.exc_info()[0]))
    return

  try:
    # as in a traditional socket, tell the system what IP addr and port are we
    # going to connect to
    connect_string = "udp://" + args.addr + ":" + str (args.port)
    print ("UDP client will be connecting to {}".format (connect_string))
    socket.connect (connect_string)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error connecting RADIO socket to DISH: {}".format (err))
    socket.close ()
    return
  except:
    print ("Some exception occurred connecting radio socket {}".format (sys.exc_info()[0]))
    socket.close ()
    return

  # since we are a client, we actively send something to the server
  print ("client sending Hello messages for specified num of iterations")
  for i in range (args.iters):
    try:
      #  Wait for next request from client
      print ("Send a HelloWorld to group {}".format (args.group))
      socket.send (b"HelloWorld", group=args.group)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error sending: {}".format (err))
      # Since an exception is getting thrown despite success, we do this
      if (err.errno != 0):
        socket.close ()
        return
      else:
        pass
    except:
      print ("Some exception occurred receiving/sending {}".format (sys.exc_info()[0]))
      socket.close ()
      return

    time.sleep (1)  # sleep 1 sec

##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
  # parse the command line
  parser = argparse.ArgumentParser ()

  # add optional arguments
  parser.add_argument ("-a", "--addr", default="localhost", help="IP Address to connect to (default: localhost i.e., 127.0.0.1)")
  parser.add_argument ("-g", "--group", default="demo", help="Group to send the message to (default: demo")
  parser.add_argument ("-i", "--iters", type=int, default=10, help="Number of iterations (default: 10")
  parser.add_argument ("-p", "--port", type=int, default=7777, help="Port that server is listening on (default: 7777)")
  args = parser.parse_args ()

  return args
    
#------------------------------------------
# main function
def main ():
  """ Main program """

  print("Demo program for UDP Client with ZeroMQ")

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
