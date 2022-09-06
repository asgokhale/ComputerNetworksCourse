# Sample code for CS4283-5283
# Vanderbilt University
# Instructor: Aniruddha Gokhale
# Created: Fall 2022
# 
# Purpose: Demonstrate a UDP-based server using traditional
# sockets
#
# See https://docs.python.org/3/library/socket.html

# import the needed packages
import sys    # for system exception
import time   # for sleep
import argparse # for argument parsing
import socket # this is the underlying socket package

##################################
# Driver program
##################################
def driver (args):
  try:
    # The first step is to obtain a socket. Here we create one in BLOCKING mode
    print ("Create a socket")
    s = socket.socket (socket.AF_INET, # this indicates we need an IPv4 style socket
                       socket.SOCK_DGRAM) # this indicates we need the best effort transport
  except OSError as err:
    print ("Exception creating a socket {}".format (err))
    return
  except:
    print ("Other exception obtaining a socket {}".format (sys.exc_info()[0]))
    return

  try:
    # The next step is to bind the socket to the interface and port on which it is
    # going to listen for incoming connections
    # This is supplied as a pair of the interface on which the server listens and the port
    print ("Bind the socket to interface: {} and port {}".format (args.intf, args.port))
    addr = (args.intf, args.port)
    s.bind (addr)
  except OSError as err:
    print ("Exception binding a socket {}".format (err))
  except:
    print ("Some exception occurred binding socket {}".format (sys.exc_info()[0]))

  # Note that in UDP, there is no listening and no connection establishment as is the
  # case in TCP. Thus, there is no new socket created. Everything is sent/received
  # on the same socket as the one used to bind.

  # Since there is no notion of a connection, we may be receiving messages from
  # any client. So we need to know whom are we receiving it from 
  while True:
    print ("Waiting to receive from some client: {}")
    try:
      message, client = s.recvfrom (1024)
      print ("Received message: {} from client: {}".format (message, client))
    except OSError as err:
      print ("Exception creating a socket {}".format (err))
    except:
      print ("Some exception occurred accepting connection {}".format (sys.exc_info()[0]))

    #  Do some 'work'. In this case we just sleep.
    time.sleep (1)

    try:
      #  Send reply back to client
      print ("Send dummy reply to the same client")
      s.sendto (b"ACK", client)
    except OSError as err:
      print ("Exception sending to client {}".format (err))
    except:
      print ("Some exception occurred sending {}".format (sys.exc_info()[0]))

  # if we ever come out of the loop, close the socket.
  s.close ()

##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
  # parse the command line
  parser = argparse.ArgumentParser ()

  # add optional arguments
  parser.add_argument ("-i", "--intf", default="", help="Interface to bind to (default: \"\"")
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

  main ()
