import socket
import threading
import json
from cmd import Cmd

class Client(Cmd):

    prompt = ''
    intro = '欢迎来到多人聊天室，输入help可获取帮助\n'

    def __init__(self):
        super().__init__()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__id = None
        self.__username = None
        self.__isLogin = False

    def __receive_message_thread(self):
        while self.__isLogin:
            # noinspection PyBroadException
            try:
                buffer = self.__socket.recv(1024).decode()
                obj = json.loads(buffer)
                print('[' + str(obj['sender_username']) + '(' + str(obj['sender_id']) + ')' + ']', obj['message'])
            except Exception:
                print('[Client] 无法从服务器获取数据')

    def __send_message_thread(self, message):
        self.__socket.send(json.dumps({
            'type': 'broadcast',
            'sender_id': self.__id,
            'message': message
        }).encode())

    def start(self):
        self.__socket.connect(('127.0.0.1', 8888))
        self.cmdloop()

    def do_login(self, args):
        username = args.split(' ')[0]
        self.__socket.send(json.dumps({
            'type': 'login',
            'username': username
        }).encode())
        try:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__username = username
                self.__id = obj['id']
                self.__isLogin = True
                print('[Client] 成功登入聊天室')
                # 开启子线程用于接受数据
                thread = threading.Thread(target=self.__receive_message_thread)
                thread.setDaemon(True)
                thread.start()
            else:
                print('[Client] 无法登入聊天室')
        except Exception:
            print('[Client] 无法从服务器获取数据')

    def do_send(self, args):
        message = args
        # 显示自己发送的消息
        print('[' + str(self.__username) + '(' + str(self.__id) + ')' + ']', message)
        # 开启子线程用于发送数据
        thread = threading.Thread(target=self.__send_message_thread, args=(message,))
        thread.setDaemon(True)
        thread.start()

    def do_logout(self, args=None):
        self.__socket.send(json.dumps({
            'type': 'logout',
            'sender_id': self.__id
        }).encode())
        self.__isLogin = False
        return True

    def do_help(self, arg=None):
        print('[Help] login (username) - 登入聊天室')
        print('[Help] send (message) - 发送消息')
        print('[Help] logout - 退出聊天室\n')