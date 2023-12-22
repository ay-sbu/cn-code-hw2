from socket import *
import threading
import os
from maclasses import MaUser

# ----------------------------------------------------------- constants
null = 'null'
seperator = ';'

# ----------------------------------------------------------- data
current_user = null

# ----------------------------------------------------------- exit page
def exit_page():
    print('bye bye')
    os._exit(0)

# ----------------------------------------------------------- chat page
def chat_page_view(chat_index):
    print()
    print('CHAT PAGE')
    current_chat = current_user.chats[chat_index]
    for i in range(len(current_chat.messages)):
        messagei = current_chat.messages[i]
        print(messagei.sender_name + ': ' + messagei.content)

def chat_page_controller(command, chat_index):
    msg = str(chat_index) + seperator + command
    client_socket.send(msg.encode())

def chat_page(chat_index):
    while True:
        client_socket.send('update_user'.encode())
        chat_page_view(chat_index)

        command = input('> ')

        if command == 'exit':
            exit_page()
        elif command == 'back':
            client_socket.send('back'.encode())
            break
        elif command == '':
            client_socket.send('continue'.encode())
            continue

        chat_page_controller(command, chat_index)

# ----------------------------------------------------------- main page
def main_page_view():
    global current_user
    print()
    print('MAIN PAGE')
    print('username: ' + current_user.username + ', ' + 'isBusy: ' + str(current_user.isBusy))
    print('Choose between chats by name: ')
    print('- send to all (all)')

    for i in range(len(current_user.chats)):
        print('-', current_user.chats[i].name)

    print()

def main_page_controller(command):
    global current_user
    client_socket.send('continue'.encode())
    for i in range(len(current_user.chats)):
        if command == current_user.chats[i].name:
            chat_page(i)
            break
    else:
        print('chat not found?!')

def main_page():
    global current_user
    client_socket.send('update_user'.encode())
    print()
    print('getting data from server...')
    data = client_socket.recv(1000000)
    print(data.decode())
    current_user = MaUser.from_json(data.decode())

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    while True:
        client_socket.send('update_user'.encode())
        main_page_view()
        try:
            command = input('> ')

            if command == 'exit':
                exit_page()

            result = main_page_controller(command)

        except Exception as e:
            print('error:', e)
            break

        print()

    receive_thread.join()

# ----------------------------------------------------------- receiving thread
def receive_messages_controller(command):
    global current_user
    ins = command.split(seperator)
    if ins[0] == 'user_data':
        current_user = MaUser.from_json(ins[1])

def receive_messages():
    # this thread is called just when user signed in successfully
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode()
            # print('notif:', message)
            receive_messages_controller(message)

        except Exception as e:
            print('error:', e)
            break

# ----------------------------------------------------------- sign up page
def sign_in_page_controller(command):
    print('server response: ' + command)
    if 'successfull' in command:
        main_page()

def sign_in_page():
    while True:
        print()
        print('SIGN IN PAGE')
        username = input('username: ')
        if username == 'exit':
            exit_page()
        elif username == 'back':
            break

        password = input('password: ')
        if password == 'exit':
            exit_page()
        elif password == 'back':
            break

        msg = 'signin' + seperator + username + seperator + password
        client_socket.send(msg.encode())

        msg = client_socket.recv(1024)
        msg = msg.decode()

        sign_in_page_controller(msg)

# ----------------------------------------------------------- sign up page
def sign_up_page_controller(command):
    print('server response: ' + command)
    if 'successfull' in command:
        main_page()

def sign_up_page():
    while True:
        print()
        print('SIGN UP PAGE')
        username = input('username: ')
        if username == 'exit':
            exit_page()
        elif username == 'back':
            break

        password = input('password: ')
        if password == 'exit':
            exit_page()
        elif password == 'back':
            break

        msg = 'signup' + seperator + username + seperator + password
        client_socket.send(msg.encode())

        msg = client_socket.recv(1024)
        msg = msg.decode()

        sign_up_page_controller(msg)

# ----------------------------------------------------------- first page
def first_page_view():
    print()
    print('FIRST PAGE')
    print('1. sign in (signin)')
    print('2. sign up (signup)')

def first_page_controller(command):
    if command == '1' or command == 'signin':
        sign_in_page()
    elif command == '2' or command == 'signup':
        sign_up_page()
    else:
        print('command not found?!')

def first_page():
    while True:
        first_page_view()
        try:
            command = input('> ')

            if command == 'exit':
                exit_page()
            elif command == 'back':
                break

            result = first_page_controller(command)

        except Exception as e:
            print('error:', e)
            break

# ----------------------------------------------------------- main
if __name__ == '__main__':
    server_ip = '127.0.0.1'
    server_port = 12_033

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    send_thread = threading.Thread(target=first_page)
    send_thread.start()
    send_thread.join()

    client_socket.close()
