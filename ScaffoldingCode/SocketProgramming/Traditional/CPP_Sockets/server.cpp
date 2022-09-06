// $Id$

#include <iostream>
#include <string>
#include <cstring>
using namespace std;              // use the "std" namespace

#ifdef _WIN32 /* windows */

#include <Winsock2.h>

#else         /* Linux, POSIX */

#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/in.h>

#endif        /* if windows */

// we define a few macros here to avoid repetitive inclusion of 
// the ifdef ... else ... end if

#ifdef _WIN32 /* windows */
// windows type for process id
#define CS4283_PID          DWORD
// windows type for exit status
#define CS4283_STATUS        DWORD
// windows socket handle
#define CS4283_SOCK_HANDLE SOCKET

// windows function to retrieve current process id
#define CS4283_GETPID()      GetCurrentProcessId ()
// windows function to exit
#define CS4283_EXIT(STATUS)  ExitProcess (STATUS)
// windows function to get current thread id

#else /* Linux */

// unix type for process id
#define CS4283_PID           int
// unix type for exit status
#define CS4283_STATUS        int
// unix socket handle
#define CS4283_SOCK_HANDLE int

// unix function to retrieve process id
#define CS4283_GETPID()      getpid ()
// unix function to exit
#define CS4283_EXIT(STATUS)  exit (STATUS)

#endif /* if windows */

// server main function
int main (int argc, char *argv[])
{ 
    // first declare the variables
    u_short port_num;               // port number is unsigned short
    CS4283_SOCK_HANDLE listen_sock;  // socket handle for listening port
    CS4283_SOCK_HANDLE conn_sock;    // socket handle for accepted connection
    sockaddr_in server_addr;        // required for bind (See below)



#ifdef       _WIN32    /* Windows */
    /* I found the hard way that on WIndows this madness has to be
       done in order to load the Ws2_32.dll. Only then can we start
       using the socket library
    */
    WORD wVersionRequested;
    WSADATA wsaData;
    int err;
 
    wVersionRequested = MAKEWORD( 2, 2 );
 
    err = WSAStartup( wVersionRequested, &wsaData );
    if ( err != 0 ) {
        /* Tell the user that we could not find a usable */
        /* WinSock DLL.                                  */
        return -1;
    }
 
    /* Confirm that the WinSock DLL supports 2.2.*/
    /* Note that if the DLL supports versions greater    */
    /* than 2.2 in addition to 2.2, it will still return */
    /* 2.2 in wVersion since that is the version we      */
    /* requested.                                        */
 
    if ( LOBYTE( wsaData.wVersion ) != 2 ||
         HIBYTE( wsaData.wVersion ) != 2 ) {
        /* Tell the user that we could not find a usable */
        /* WinSock DLL.                                  */
        WSACleanup( );
        return -1; 
    }

#endif                 /* end windows */

    // you must first parse the command line arguments if any
    // **** ADD CODE HERE ***


    /* Now let us initialize the server */

    // in order to ensure that there is no conflict on the listen
    // port, I am going to use the process ID, which is unique on the
    // OS, and add 10000 to it.
    port_num = 10000 + (u_short)CS4283_GETPID ();
    cout << "Server will use port = "
         << port_num << endl;

    // STEP (1)
    // initialize the socket for the port we will listen on
    // A socket is a handle created by the operating system that
    // serves as the "end-point" through which network I/O can be
    // performed. Note, however, that simply creating a socket handle
    // does not immediately allow the server to start receiving client
    // requests. As shown in the different steps below, the socket
    // handle must first be associated with the network interface of
    // the machine. Only then can you start listening for incoming
    // requests. When a client sends a "connection establish" request,
    // the server will accept it using the "accept" command shown
    // below. Therefter the client and server exchange messages until
    // the session is over in which case both parties close the socket
    // handles.
    listen_sock = socket (AF_INET,      // use IPv4 family
                          SOCK_STREAM,  // full duplex byte stream
                          0);           // protocol type (TCP)

    // error checking
#ifdef    _WIN32  /* Windows */
    if (listen_sock == INVALID_SOCKET) {
        cerr << "Server: socket call failed" << endl;
        return -1;
    }
#else             /* LINUX */
    if (listen_sock == -1) {
        perror ("socket failed");
        cerr << "Server: socket call failed" << endl;
        return -1;
    }
#endif            /* if windows */

                          
    // STEP (2)
    // now we need to bind the socket handle to the network interface
    // over which we intend to receive incoming requests. The use of
    // INADDR_ANY shown below indicates that we will receive request
    // over any network interface that this machine has.
    // To do this we must first initialize a structure whose type is
    // "struct sockaddr_in"
    //
    // (2a) first make sure we reset the structure. We do not want any
    // garbage values in this structure.
    memset (&server_addr, 0, sizeof (sockaddr_in));

    // (2b) set the fields of the structure

    // first indicate the addressing family. We choose IP version 4.
    server_addr.sin_family = AF_INET;   // IPv4 family

    // see how we use INADDR_ANY to indicate we will receive requests
    // over all interfaces. Also note how we use the function
    // "htonl". This function converts data from native type to
    // network type. The "htonl" indicates conversion of a "long" from
    // host to network byte order
    // The architecture of the CPU on our machine could be little
    // endian or big endian. Intel Pentiums are little-endian
    // machines whereas Sun Sparc or PowerPC chips are big endian.
    //
    // The protocol standardizing committee decided to use
    // "big-endian" as the byte order of any data that goes over the
    // network. Therefore, every time any data must be shipped has to
    // be converted between the host format (which could be little or
    // big endian) and the network format (which is big endian).
    // The OS provides utility functions called "htonl" (and
    // correspondingly "ntohl") to convert a "long" value in host byte
    // order to "long" value in network byte order (note that "ntohl"
    // will do the reverse action). For "short" data type we have
    // "htons" and "ntohs". Nothing needs to be done for "char"
    server_addr.sin_addr.s_addr = htonl (INADDR_ANY);

    // indicate what port number we will be listening on
    // once again see how we convert the data into network byte
    // order. This time we use htons since port_num is a "short"
    server_addr.sin_port = htons (port_num);
    
    // (2c) Now actually make the association of the socket to the address 
    // via the "bind" call 
    int bind_status;
    bind_status =
        bind (listen_sock,    // this was the listen socket handle we
                              // created earlier
              // the second arg is supposed to be of type "sockaddr"
              // which is a typedef declared in the OS headers to 
              // represent a generic network family. However, we 
              // are using the IPv4 family and hence had initialized
              // the "sockaddr_in" structure. Therefore, now we must
              // cast the sockaddr_in to sockaddr
              //
              // Note we cannot use "static_cast" since the two types
              // are different. Therefore, we ask the compiler to 
              // reinterpret the type by using the C++
              // reinterpret_cast command
              reinterpret_cast<sockaddr *> (&server_addr),
              // indicate the size of the structure
              sizeof (sockaddr));

    // error checking
#ifdef    _WIN32  /* Windows */
    if (bind_status == SOCKET_ERROR ) {
        cerr << "Server: bind failed" << endl;
        return -1;
    }
#else             /* LINUX */
    if (bind_status == -1 ) {
        perror ("bind failed");
        cerr << "Server: bind failed" << endl;
        return -1;
    }
#endif            /* if windows */

    // STEP 3: Now indicate to the OS that the server is ready to
    // start listening for incoming connection establishment requests
    // from clients.
    int listen_status;
    listen_status = listen (listen_sock, // our listen sockethandle
                            5);          // backlog parameter (don't worry)

    // error checking
#ifdef    _WIN32  /* Windows */
    if (listen_status == SOCKET_ERROR) {
        cerr << "Server: listen failed" << endl;
        return -1;
    }
#else             /* LINUX */
    if (listen_status == -1) {
        perror ("listen failed");
        cerr << "Server: listen failed" << endl;
        return -1;
    }
#endif            /* if windows */

    // STEP 4: Now accept any incoming connection. Note that we are a
    // server and hence we are supposed to accept connections and serve 
    // the client requests. Most likely the service we provide is a long 
    // living service. Therefore, we do the following logic inside an
    // infinite loop
    for (;;) {
        cout << "Server: WAITING TO ACCEPT A NEW CONNECTION" << endl;

        // the accept command shown below actually does the job of
        // the TCP/IP 3-way handshaking protocol when a client
        // requests a connection establishment.
        //
        // Note that the accept command creates a new socket handle as
        // the return value of "accept". Understand that this is
        // necessary because in order to serve several clients
        // simultaneously, the server needs to distinguish between
        // the handle it uses to listen for new connections requests
        // and the handle it uses to exchange data with the
        // client. Thus, the newly created socket handle is used to do
        // the network I/O with client whereas the older socket handle 
        // continues to be used for listening for new connections.
        conn_sock = accept (listen_sock, // our listen sock handle
                            0,  // we don't care about details of client
                            0); // hence length = 0

        // error checking
#ifdef    _WIN32  /* Windows */
        if (listen_status == INVALID_SOCKET) {
            cerr << "Server: accept failed" << endl;
            return -1;
        }
#else             /* LINUX */
        if (listen_status == -1) {
            perror ("accept failed");
            cerr << "Server: accept failed" << endl;
            return -1;
        }
#endif            /* if windows */

        cout << "Server: ACCEPTED A NEW CONNECTION" << endl;

        // The I/O with client starts here. However, if we do it here,
        // then the server will be blocked until this client is
        // done. We cannot achieve concurrency doing I/O with client while
        // simulataneously listening for new client connections. 
        // A way out is to either fork of a child process to deal
        // with the client or spawn a thread or hand over the client 
        // request to a thread while the main thread keeps listening for
        // new requests.

        // In this case we just showcase an interative server wherein
        // a server serves one client at a time.

        char data_buff [1024];  // define a buffer to hold client data
        memset (data_buff, 0, sizeof (data_buff)); // clear its contents

        int recv_status = recv (conn_sock,  // client I/O to be done
                                            // with new socket
                                // second parameter is a buffer into
                                // which you receive data
                                // Windows needs a (char *) buffer
                                // while Linux needs a (void *) buffer
                                // hence we have to do the following
#ifdef    _WIN32  /* Windows */
                                (char *)data_buff,
#else             /* LINUX */
                                (void *)data_buff,
#endif            /* if windows */
                                // third parameter is the size of the
                                // buffer
                                sizeof (data_buff),
                                // last parameter is a flag that we
                                // will ignore.
                                0);

        // network I/O is tricky. Sometime you do not receive all the
        // bytes you have requested. I am not going to check for this
        // condition. On Linux you can force the kernel to not return
        // until all the requested bytes are read by using a special
        // flag that does not seem to be available on Windows.
        // The only error checking that we do is thus failed "recv"
#ifdef    _WIN32  /* Windows */
        if (recv_status == SOCKET_ERROR) {
            cerr << "Server: recv failed" << endl;
            return -1; // note we should really cleanup but we ignore it
        }
#else             /* LINUX */
        if (recv_status == -1) {
            perror ("recv failed");
            cerr << "Server: recv failed" << endl;
            return -1; // note we should really cleanup but we ignore it
        }
#endif            /* if windows */

        cout << "Server: Received: " << data_buff << endl;

        // we just send this back to client :-)

        int send_status = 
            send (conn_sock, // I/O is done on this socket handle
                  // second parameter is the buffer you send
#ifdef    _WIN32  /* Windows */
                  (const char *) data_buff,
#else             /* LINUX */
                  (void *) data_buff,
#endif            /* if windows */
                  // 3rd param is the length of the buffer
                  sizeof (data_buff),
                  // we ignore the flags argument
                  0);
        
        // error checking
#ifdef    _WIN32  /* Windows */
        if (send_status == SOCKET_ERROR) {
            cerr << "Server: send failed" << endl;
            return -1; // note we should really cleanup but we ignore it
        }
#else             /* LINUX */
        if (send_status == -1) {
            perror ("send failed");
            cerr << "Server: send failed" << endl;
            return -1; // note we should really cleanup but we ignore it
        }
#endif            /* if windows */

        // STEP 6: close the new handle because we are done with the client
#ifdef    _WIN32  /* Windows */
        (void) closesocket (conn_sock);
#else             /* LINUX */
        (void) close (conn_sock);
#endif            /* if windows */


        // we make a policy decision that if we receive the string "exit" 
        // from the client, we are going to quit
        string s (data_buff);
        if (s.compare ("exit") == 0) {
            cout << "Server is EXITING" << endl;
            break;
        }
    } // end of for loop


    // cleanup the listening endpoint
#ifdef    _WIN32  /* Windows */
    (void) closesocket (listen_sock);

    WSACleanup ();
#else             /* LINUX */
    (void) close (listen_sock);
#endif            /* if windows */

    return 0;
}
