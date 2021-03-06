# Socket server in python using select function

import socket, select
from time import gmtime, strftime

def create_file(timestamp, index):
    f = open("data/" + timestamp + "-" + str(index) + ".csv","w+")
    return f

def write_to_file(data, FILE):
    FILE.write(data)

def main():
    CONNECTION_LIST = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000
    FILE = None
    FILE_COUNT = 1
    MAX_FILE_SIZE = 200
    CUR_FILE_SIZE = -1
    TIMESTAMP = None


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    print("Server started on port " + str(PORT))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

        for sock in read_sockets:

            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print("Client (%s, %s) connected" % addr)

                # saving timestamp of connection time
                TIMESTAMP = strftime("%y-%m-%d-%H:%M:%S", gmtime())

                # Create new CSV file with timestamp of the connection
                FILE = create_file(TIMESTAMP, FILE_COUNT)

            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    if data and FILE:
                        CUR_FILE_SIZE += 1
                        if CUR_FILE_SIZE >= MAX_FILE_SIZE :
                            FILE_COUNT += 1
                            CUR_FILE_SIZE = 0
                            FILE.close()
                            FILE = create_file(TIMESTAMP, FILE_COUNT)
                        write_to_file(data, FILE)

                # client disconnected, so remove from socket list
                except:
                    broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    print("Client (%s, %s) is offline" % addr)
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue

    server_socket.close()

if __name__ == "__main__":
    main()
