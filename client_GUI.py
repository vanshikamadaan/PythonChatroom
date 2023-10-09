import tkinter
from tkinter import messagebox, ttk
try:
    from ttkthemes import ThemedTk
except:
    pass
import socket
import sys
import _thread
import pickle


IP = "apnachatroom69.ddns.net"
IP = "localhost"
IP ="apnachatroom.noice.me"
IP = "192.168.0.165"
port = 6969

headerLength = 10
serverUsername = "server"
username = ""
quit =  None
guiLoaded = False
guiTheme = "breeze"

# Connecting to server

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    c.connect((IP, port))
except:
    try:
        root = ThemedTk(theme=guiTheme)
    except:
        root = tkinter.Tk()
    root.title("Chatroom")
    ttk.Label(root, text="Server is offline.").pack(padx=50, pady=50)
    root.mainloop()
    sys.exit()



def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        global quit
        msg = "close"
        c.send((f"{len(msg):<{headerLength}}" + msg).encode('utf-8'))
        c.close()
        quit = True
        
def recieveMessageHistory(sock):
    messageHeader = sock.recv(headerLength).decode('utf-8')
    if messageHeader:
        messageLength = int(messageHeader.strip())
        messageHistoryEncoded = sock.recv(messageLength)
        messageHistory = pickle.loads(messageHistoryEncoded)
        for msg in messageHistory:
            cursorIndex = 0
            usernameHeader = int(msg[cursorIndex : headerLength].strip())
            cursorIndex += headerLength
            usernameOfMsg = msg[cursorIndex : cursorIndex + usernameHeader]
            cursorIndex += usernameHeader
            msgHeader = int(msg[cursorIndex : cursorIndex + headerLength])
            cursorIndex += headerLength
            message = msg[cursorIndex : cursorIndex + msgHeader]
            if usernameOfMsg == serverUsername:
                addItem(message)
            else:
                addItem(f"{usernameOfMsg}=>{message}")
    
def recieveMsg(sock):
    recvUsernameHeader = sock.recv(headerLength).decode('utf-8')
    if not recvUsernameHeader:
        return False
    recvUsernameLength = int(recvUsernameHeader.strip())
    recvUsername = sock.recv(recvUsernameLength).decode('utf-8')
    messageHeader = sock.recv(headerLength).decode('utf-8')
    if not messageHeader:
        return False
    messageLength = int(messageHeader.strip())
    message = sock.recv(messageLength).decode('utf-8')
    return (recvUsername, message)

def recieveFromServer(sock):
    messageHeader = sock.recv(headerLength).decode('utf-8')
    if not messageHeader:
        return False
    messageLength = int(messageHeader.strip())
    message = sock.recv(messageLength).decode('utf-8')
    return message

def addItem(msg=None):
    global chat, msgEntry
    if msg is None:
        msg = msgEntry.get()
        if msg == "":
            return
        c.send((f"{len(msg):<{headerLength}}" + msg).encode('utf-8'))
        msg = username + "=>" + msg
        msgEntry.delete(0, len(msg))
    chat.insert("end", msg)
    chat.yview("end")

def returnPressed(event):
    addItem()



# Thread 1
def gui(threadName, delay):
    global chat, msgEntry, response, guiLoaded

    try:
        root = ThemedTk(theme=guiTheme)
    except:
        root = tkinter.Tk()
    root.title("Chatroom")
     
    ttk.Label(root, text=response).pack()

    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=10)

    chat = tkinter.Listbox(frame, width=50, height=20)
    scrollbar = ttk.Scrollbar(frame) 

    scrollbar.pack(side="right", fill="y")
    chat.pack(side="left", fill="y") 

    chat.configure(yscrollcommand = scrollbar.set)
    scrollbar.configure(command = chat.yview)

    entryFrame = ttk.Frame(root)
    entryFrame.pack(padx=10, pady=10)

    msgEntry = ttk.Entry(entryFrame)
    msgEntry.grid(row="0", column="0")

    submitEntry = ttk.Button(entryFrame, text="Send", command=addItem)
    submitEntry.grid(row="0", column="1")

    root.bind('<Return>', returnPressed)
    root.protocol("WM_DELETE_WINDOW", on_closing)

    guiLoaded = True

    root.mainloop()

# Thread 2

def recvMsgs(threadName, delay):
    while True:
        try:
            newMsg = recieveMsg(c)
            if newMsg and newMsg[0] == serverUsername:
                addItem(newMsg[1])
            elif newMsg:
                addItem(f"{newMsg[0]}=>{newMsg[1]}")
        except:
            pass
def getUsername():
    global usernameEntry, username
    username = usernameEntry.get()
    root.destroy()


# Input username


try:
    root = ThemedTk(theme=guiTheme)
except:
    root = tkinter.Tk()
root.title("Chatroom")
root.title("Enter username")

entryFrame = ttk.Frame(root)
entryFrame.pack(padx=100, pady=50)

ttk.Label(entryFrame, text="Enter your username:").grid(row=0, column=0)

usernameEntry = ttk.Entry(entryFrame)
usernameEntry.grid(row="0", column="1")

submitEntry = ttk.Button(entryFrame, text="Go", command=getUsername)
submitEntry.grid(row="0", column="2")

root.mainloop()


c.send((f"{len(username):<{headerLength}}" + username).encode('utf-8'))

response = recieveFromServer(c)
# response = "test"
if response == "username error":
    try:
        root = ThemedTk(theme=guiTheme)
    except:
        root = tkinter.Tk()
    root.title("Chatroom")
    messagebox.showerror("Error", "Invalid username")
    root.destroy()
    root.mainloop()
    c.close()
    sys.exit()




# Create two threads as follows
try:
    _thread.start_new_thread( gui, ("Thread-1", 2, ) )
    
    while not guiLoaded:
        pass

    recieveMessageHistory(c)
    _thread.start_new_thread( recvMsgs, ("Thread-2", 4, ) )
except Exception as err:
    print("Error:", err)


while not quit:
    pass


