import socket
import select
import sys
import time
import pickle


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

IP = get_ip()
port = 6969

headerLength = 10

def recieveMsg(sock):
    try:
        messageHeader = sock.recv(headerLength).decode('utf-8')
        if not messageHeader:
            return False
        messageLength = int(messageHeader.strip())
        message = sock.recv(messageLength).decode('utf-8')
        return message
    except:
        return False

def broadcast(notified_socket, message):
    for sock in socketList:
        username = clients[notified_socket]
        if sock != notified_socket and sock != serverSock and not sock._closed:
            data = f"{len(username):<{headerLength}}" + username + f"{len(message):<{headerLength}}" + message
            try:
                sock.send(data.encode('utf-8'))
            except:
                return False

def sendMsg(sock, message):
    data = f"{len(message):<{headerLength}}" + message
    sock.send(data.encode('utf-8'))

def addToMessageHistory(username, message):
    messageHistory.append(f"{len(username):<{headerLength}}" + username + f"{len(message):<{headerLength}}" + message)



serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socketList = [serverSock]
clients = {serverSock: "server"}
messageHistory = []

serverSock.bind((IP, port))

while True:
    try:
        serverSock.listen()
        print(f"Listening at {IP}...")
        while True:
            read_sockets, _, exception_sockets = select.select(socketList, [], socketList)

            for notified_socket in read_sockets:
                if notified_socket == serverSock:
                        sock, ip = serverSock.accept()
                        time.sleep(0.2)
                        username = recieveMsg(sock)
                        if not username or username == "server":
                            sendMsg(sock, "username error")
                            sock.close()
                            if sock in socketList:
                                socketList.remove(sock)
                            print(ip, "Disconnected due to invaild username")
                            continue
                        sendMsg(sock, "Welcome to the chatroom!")
                        socketList.append(sock) 
                        clients[sock] = username
                        print(username, ip , "connected")
                        addToMessageHistory(clients[notified_socket], f"{username} connected.")
                        encodedData = pickle.dumps(messageHistory)
                        sock.send( f"{len(encodedData):<{headerLength}}".encode('utf-8') + encodedData)
                else:
                    message = recieveMsg(notified_socket)
                    if message and message.strip() != "":
                        if message == "close":
                            broadcast(serverSock, f"{username} disconnected.")
                            print(username, "disconnected")
                            addToMessageHistory(clients[serverSock], f"{username} disconnected.")
                            sock.close()
                            if sock in socketList:
                                socketList.remove(sock)
                            break
                        else:
                            broadcast(notified_socket, message)
                            addToMessageHistory(clients[notified_socket], message)
                        print(clients[notified_socket], "-", message)
                for notified_socket in exception_sockets:
                    # Remove from list for socket.socket()
                    socketList.remove(notified_socket)
    except KeyboardInterrupt:
        print("Closing server...")
        input()
        break
    except Exception as error:
        print("Error!!" ,error)
        input()
        sys.exit()
