// $Id$

#include <iostream>
#include <string>
#include <cstring>
using namespace std;

#ifdef    _WIN32  /* Windows */

#include <Winsock2.h>       // all the socket stuff

#else             /* LINUX */

#include <sys/types.h>      // for various data types
#include <sys/socket.h>     // for socket API
#include <netinet/in.h>     // for sockaddr_in
#include <arpa/inet.h>      // for inet_addr
#include <unistd.h>         // for getpid ()
#include <sys/time.h>       // for timing

#endif            /* if windows */

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


/* 
   The client, very similar to the server, has to do some
   initialization in order to establish connection with server and do
   network I/O.
*/

// client main function
int main (int argc, char *argv[])
{ 
    // first declare the variables
    u_short port_num;               // port number is unsigned short
    char dotted_form [15];          // IP addr of server in dotted form
    CS4283_SOCK_HANDLE conn_sock;    // socket handle for connection
    sockaddr_in server_addr;        // required for connect (See below)

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

    /**************** real program starts here **************/

    // **** ADD CODE HERE *** if you have any command line parsing to
    // do such as passing the port number of the server or IP address
    // of server. In our case I am going to ask the user to input it.


    /* Now let us initialize the client */

    cout << "Enter server's port number: ";
    cin >> port_num;

    // to find out what is the ip address of the server, open a shell
    // on the OS you are working on and type:
    // ipconfig /all     (this works on windows)
    //
    // or
    //
    // netstat -i        (this works on Linux)
    //
    cout << "Enter server's IP address (dotted decimal form): ";
    cin >> dotted_form;

    // STEP (1)
    // initialize the socket for the port we will use to connect to
    // server and do I/O
    conn_sock = socket (AF_INET,      // use IPv4 family
                        SOCK_STREAM,  // full duplex byte stream
                        0);           // protocol type (TCP)

    // error checking
#ifdef    _WIN32  /* Windows */
    if (conn_sock == INVALID_SOCKET) {
        cerr << "Client: socket call failed" << endl;
        return -1;
    }
#else             /* LINUX */
    if (conn_sock == -1) {
        perror ("socket failed");
        cerr << "Client: socket call failed" << endl;
        return -1;
    }
#endif            /* if windows */

                          
    // STEP (2)
    // Now we must connect to the server. 
    // A client is considered to be the active entity because it
    // initiates a dialog with the server. On the other hand the
    // server is a passive entity
    //
    // (2a) first make sure we reset the structure. We do not want any
    // garbage values in this structure.
    memset (&server_addr, 0, sizeof (sockaddr_in));

    // (2b) set the fields of the structure

    // first indicate the addressing family. We choose IP version 4.
    server_addr.sin_family = AF_INET;   // IPv4 family

    // set the network address of the server. Note that the address we
    // used was a dotted decimal string that is understandable by
    // humans. But it is not understood by the network API. It needs
    // the network address in a different format. That is why we use
    // the "inet_addr" utility function. Note that the returned value
    // is already in network byte order. So you do not yet again
    // convert it.
    server_addr.sin_addr.s_addr = inet_addr (dotted_form);

    // error check
    if (server_addr.sin_addr.s_addr == INADDR_NONE) {
        cerr << "Client: inet_addr failed" << endl;
        return -1;
    }

    // indicate what port number of server
    // We convert the data into network byte
    // order. This time we use htons since port_num is a "short"
    server_addr.sin_port = htons (port_num);
    
    // (2c) Now actively establish connection
    int conn_status;
    conn_status =
        connect (conn_sock,    // this was the connection socket handle we
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
    if (conn_status == SOCKET_ERROR ) {
        cerr << "Client: connect failed" << endl;
        return -1;
    }
#else             /* LINUX */
    if (conn_status == -1 ) {
        perror (" failed");
        cerr << "Server: connect failed" << endl;
        return -1;
    }
#endif            /* if windows */

    cout << "Client: ESTABLISHED A CONNECTION" << endl;

    // send and receive some data
    char send_buff [1024];
    char rcv_buff [1024];

    memset (send_buff, 0, sizeof (send_buff));
    cout << "Enter data to send to server (enter exit to kill server): ";
    cin >> send_buff;

    int send_status = 
        send (conn_sock, // I/O is done on this socket handle
              // second parameter is the buffer you send
#ifdef    _WIN32  /* Windows */
              (const char *) send_buff,
#else             /* LINUX */
              (void *) send_buff,
#endif            /* if windows */
                  // 3rd param is the length of the buffer
              sizeof (send_buff),
              // we ignore the flags argument
              0);
        
    // error checking
#ifdef    _WIN32  /* Windows */
    if (send_status == SOCKET_ERROR) {
        cerr << "Client: send failed" << endl;
        return -1; // note we should really cleanup but we ignore it
    }
#else             /* LINUX */
    if (send_status == -1) {
        perror ("send failed");
        cerr << "Client: send failed" << endl;
        return -1; // note we should really cleanup but we ignore it
    }
#endif            /* if windows */

    memset (rcv_buff, 0, sizeof (rcv_buff));

    // Now we expect the server to send us a reply. So we block until
    // we receive something
    int recv_status = recv (conn_sock,  // I/O done with new sock
                            // handle
                            // second parameter is a buffer into
                            // which you receive data
                            //
                            // Windows needs a (char *) buffer
                            // while Linux needs a (void *) buffer
                            // hence we have to do the following
#ifdef    _WIN32  /* Windows */
                            (char *) rcv_buff,
#else             /* LINUX */
                            (void *) rcv_buff,
#endif            /* if windows */
                            // third parameter is the size of the
                            // buffer
                            sizeof (rcv_buff),
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
        cerr << "Client: recv failed" << endl;
        return -1; // note we should really cleanup but we ignore it
    }
#else             /* LINUX */
    if (recv_status == -1) {
        perror ("recv failed");
        cerr << "Client: recv failed" << endl;
        return -1; // note we should really cleanup but we ignore it
    }
#endif            /* if windows */


    cout << "Client received: " << rcv_buff << endl;

    // STEP 6: close the handle because we are done
#ifdef    _WIN32  /* Windows */
    (void) closesocket (conn_sock);
    
    WSACleanup ();
#else             /* LINUX */
    (void) close (conn_sock);
#endif            /* if windows */


    return 0;
}
