# Sample code for CS4283-5283
# Vanderbilt University
# Instructor: Aniruddha Gokhale
# Created: Fall 2022
# 
# Purpose: Demonstrate a TCP-based server using traditional
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
                       socket.SOCK_STREAM) # this indicates we need a reliable stream style socket
  except OSError as err:
    print ("Exception creating a socket {}".format (err))
  except:
    print ("Other exception obtaining a socket {}".format (sys.exc_info()[0]))

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

  try:
    # The next step is to enable the socket to listen for incoming connections
    print ("Listen for incoming connections")
    s.listen ()
  except OSError as err:
    print ("Exception listening {}".format (err))
  except:
    print ("Some exception occurred listening {}".format (sys.exc_info()[0]))

  # since we are a server, we service incoming clients forever. But this is where
  # things can go crazy. For every incoming connection, the server generates a new
  # connection to the client. To server multiple clients at once, we will need
  # concurrent handling, e.g., using process per connection or thread per connection
  # or via thread pool. But here we will do an iterative server handling only one
  # client at a time.
  while True:
    print ("Server now waiting to receive the next connection request")
    try:
      # the accept call returns two results: a new socket to talk to the
      # client and the address information of the client
      conn, client = s.accept ()
      print ("Connected client info = {}".format (client))
    except OSError as err:
      print ("Exception accepting a connection {}".format (err))
      continue
    except:
      print ("Some exception occurred accepting connection {}".format (sys.exc_info()[0]))
      continue

    # Now keep the session with the client on until the client decides to exit
    while True:
      try:
        # Wait for next request from client. Since we do not know how much data
        # will come from the other side, we just create some sized buffer and receive
        # whatever shows up. It is possible that there will be more.
        #
        # Notice, also that the data communication happens on the new socket and not
        # the original socket
        print ("Waiting to receive from client: {}".format (client))
        message = conn.recv (1024)
        if not message:
          # this is an indication that client closed the connection
          print ("Client closed the connection ?")
          break
        print("Received request from client: {}".format (message))
      except OSError as err:
        print ("Exception creating a socket {}".format (err))
      except:
        print ("Some exception occurred accepting connection {}".format (sys.exc_info()[0]))

      #  Do some 'work'. In this case we just sleep.
      time.sleep (1)

      try:
        #  Send reply back to client
        print ("Send dummy reply")
        conn.send (b"ACK")
      except OSError as err:
        print ("Exception sending to client {}".format (err))
      except:
        print ("Some exception occurred sending {}".format (sys.exc_info()[0]))


    # since we are out of this loop due to client closing the connection,
    # we close the client's socket here too
    print ("Closing connection to the client")
    conn.close ()

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
