import json
from types import SimpleNamespace

class MaUser:
    def __init__(self, username, password, isBusy, chats):
        self.username = username
        self.password = password
        self.isBusy = isBusy
        self.chats = chats

    def to_json(self):
        data = {
            'username': self.username,
            'password': self.password,
            'isBusy': self.isBusy,
            'chats': [MaChat.to_json(i) for i in self.chats]
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        username = data['username']
        password = data['password']
        isBusy = data['isBusy']
        chats_data = data['chats']
        chats = [MaChat.from_json(i) for i in chats_data]
        return cls(username, password, isBusy, chats)

class MaChat:
    def __init__(self, name, chat_type, isBusy, messages):
        self.name = name
        self.type = chat_type
        self.isBusy = isBusy
        self.messages = messages

    def to_json(self):
        data = {
            'name': self.name,
            'type': self.type,
            'isBusy': self.isBusy,
            'messages': [i.to_json() for i in self.messages]
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        name = data['name']
        chat_type = data['type']
        isBusy = data['isBusy']
        messages_data = data['messages']
        messages = [MaMessage.from_json(i) for i in messages_data]
        return cls(name, chat_type, isBusy, messages)

class MaMessage():
    def __init__(self, content, sender_name):
        self.content = content
        self.sender_name = sender_name

    def to_json(self):
        data = {
            'content': self.content,
            'sender_name': self.sender_name
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(data['content'], data['sender_name'])
