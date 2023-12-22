from socket import *
import threading
from maclasses import MaUser, MaChat, MaMessage

null = 'null'
seperator = ';'

# ----------------------------------------------------------- data
users = []
users_sockets = []
online_users = [] # user indexes
all_chats = []

# ----------------------------------------------------------- checkers
def do_sign_in(username, password):
    for i in range(len(users)):
        if users[i].username == username:
            if users[i].password == password:
                return i
            break
    return -1

def username_is_available(username):
    for i in range(len(users)):
        if users[i].username == username:
            return False
    return True

def do_sign_up(username, password):
    if not username_is_available(username):
        return -1

    newuser = MaUser(username, password, False, [])
    users.append(newuser)
    users_sockets.append(null)
    user_index = len(users) - 1

    for i in range(len(users)):
        if i != user_index:
            newchat = MaChat(users[user_index].username + '&' + users[i].username, 'pv', users[i].isBusy, [])
            users[user_index].chats.append(newchat)
            users[i].chats.append(newchat)

    return user_index

# ----------------------------------------------------------- message sender
def message_controller(user_index, command):
    global users
    ins = command.split(seperator)

    chat_index = int(ins[0])

    if users[user_index].chats[chat_index].isBusy:
        msg = 'notif' + seperator + 'chat is busy!'
        users_sockets[user_index].send(msg.encode())
    else:
        message = MaMessage(ins[1], users[user_index].username)
        users[user_index].chats[chat_index].messages.append(message)

# ----------------------------------------------------------- handle client
def main_page_handler(user_index):
    global users
    users_sockets[user_index] = connection_socket
    users_sockets[user_index].recv(1024)
    user_data = users[user_index].to_json()
    users_sockets[user_index].send(user_data.encode())

    while True:
        # update user data
        users_sockets[user_index].recv(1024)
        user_data = 'user_data' + seperator + users[user_index].to_json()
        users_sockets[user_index].send(user_data.encode())

        # sending messages or message_like
        command = users_sockets[user_index].recv(1024)
        command = command.decode()
        if command == 'toggle_busy':
            print('i am here')
            users[user_index].isBusy = not users[user_index].isBusy
            for i in range(len(users[user_index].chats)):
                users[user_index].chats[i].isBusy = not users[user_index].chats[i].isBusy
        elif command == 'message_like':
            continue
        else:
            print('command', command)
            message_controller(user_index, command)

def first_page_handler(connection_socket, addr):
    while True:
        command = connection_socket.recv(1024)
        command = command.decode()
        commands = command.split(';')

        s_response = 'default s_response'
        if len(commands) != 3:
            s_response = 'first page commands seperates is not 3?!'
            print(s_response)
            connection_socket.send(s_response.encode())
        elif commands[0] == 'signin':
            username, password = commands[1], commands[2]
            user_index = do_sign_in(username, password)
            if user_index != -1:
                s_response = 'signed in successfully!!'
                print(s_response)
                connection_socket.send(s_response.encode())
                main_page_handler(user_index)
            else:
                s_response = 'useranme or password is wrong.'
                print(s_response)
                connection_socket.send(s_response.encode())
        elif commands[0] == 'signup':
            username, password = commands[1], commands[2]
            user_index = do_sign_up(username, password)
            if user_index != -1:
                s_response = 'signed up successfully!!'
                print(s_response)
                connection_socket.send(s_response.encode())
                main_page_handler(user_index)
            else:
                s_response = 'useranme is not available.'
                print(s_response)
                connection_socket.send(s_response.encode())
        else:
            s_response = 'first page bad request type?!'
            print(s_response)
            connection_socket.send(s_response.encode())


# ----------------------------------------------------------- main
if __name__ == '__main__':
    server_ip = '127.0.0.1'
    server_port = 12_038

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)

    print('server is running on', server_ip + ':' + str(server_port))

    while 1:
        connection_socket, addr = server_socket.accept()
        print('new connection was accepted', 'address:', addr)
        client_thread = threading.Thread(target=first_page_handler, args=(connection_socket, addr))
        client_thread.start()
