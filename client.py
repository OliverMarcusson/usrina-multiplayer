import socket as s
from time import sleep
from ursina import *
from random import randint
import json
from threading import Thread

class Player(Entity):
    def __init__(self, username, client_socket, remote=False, add_to_scene_entities=True, **kwargs):
        super().__init__(add_to_scene_entities, **kwargs)
        
        self.username = username
        self.socket = client_socket
        self.id = int(self.socket.recv(1024).decode())
        self.socket.send(username.encode())
        
        if not remote:
            self.update = self.player_update
            self.input = self.player_input
            
            self.sender_thread = Thread(target=self.sender)
            self.sender_thread.name = f"{self.username}: sender"
            self.sender_thread.start()
        else:
            self.update = self.reciever
        
    
    def player_update(self):
        if held_keys['left arrow']:
            self.x -= 0.05
        
        if held_keys['right arrow']:
            self.x += 0.05
            
        if held_keys['up arrow']:
            self.y += 0.05
            
        if held_keys['down arrow']:
            self.y -= 0.05
            
        if held_keys['u']:
            self.scale_x += 0.05
            self.scale_y += 0.05
            self.scale_z += 0.05
        
        if held_keys['j']:
            self.scale_x -= 0.05
            self.scale_y -= 0.05
            self.scale_z -= 0.05
            
    
    def player_input(self, key):
        if key == "space":
            self.color = color.rgb(randint(0, 255), randint(0, 255), randint(0, 255))
    
    def sender(self):
        while True:
            data = json.dumps([self.x, self.y, self.scale, self.color]).encode()
            self.socket.send(data)
            sleep(0.015625)
    
    def reciever(self):
        data: list = json.loads(self.socket.recv(1024).decode())
        
        self.x = data[0]
        self.y = data[1]
        self.scale = data[2]
        self.color = data[3]
        sleep(0.015625)

def get_players(client_socket: s.socket, players: list[Player]):
    client_socket.send("id".encode())
    while True:
        data = json.loads(client_socket.recv(1024).decode())
        if data[0] == "id":
            ids = data[1]
    
def game():
    username = input("Username:")
    client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 5432))
    
    app = Ursina()
    window.title = "Cube game"
    
    players = []
    my_player = Player(username, client_socket, model="cube", scale=(1,1,1), color=color.red, origin=(0, 0))
    players.append(my_player)
    
    
    app.run()
    
def chat():
    username = input("Username:")

    client = s.socket(s.AF_INET, s.SOCK_STREAM)
    client.connect(("127.0.0.1", 5432))
    client.send(username.encode())

    while True:
        message = input("To send:")
        client.send(message.encode())
        print("Message sent.")
        sleep(1) 

def main():
    print("---| Client Selector |---\n1. Chat\n2. Game")
    
    match input(":"):
        case "2":
            game()
        case _:
            chat()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
