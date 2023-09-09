import socket as s
from threading import Thread
from time import sleep
import keyboard

# class Player:
#     def __init__(self) -> None:
#         self.x: int = 0
#         self.y: int = 0
#         self.color: list[int] = [255, 0, 0]
#         self.scale: list[int] = [1, 1, 1]

class Client:
    def __init__(self, username, socket, address) -> None:
        self.username: str = username
        self.socket: s.socket = socket
        self.address: str = address
        self.messagelog: list[str] = []
        self.handler: Thread = Thread(target=self.handler)
        self.handler.name = self.username
        self.handler.start()
    
    def handler(self):
        while True:
            data = self.socket.recv(1024)
            
            if not data:
                break
            
            message = data.decode()
            self.messagelog.append(message)
            print(f"{self.username}: {message}")

# def client_handler(client: Client):
    
def accept_clients(server: s.socket, clients: list[Client], connections: list[int], startup: list[bool]):
    while True:
        try:
            client_socket, client_adress = server.accept()
        except OSError:
            break
        
        client = Client(client_socket.recv(1024).decode(), client_socket, client_adress)
        print(f"[!] Client '{client.username}' connected.")
        
        if len(clients) == 0:
            startup[0] = False
        else:
            print(f"clients len: {len(clients)}")
        
        clients.append(client)
        connections[0] += 1
    
def heartbeat(clients: list[Client], connections: int):
    while True:
        if not len(clients) == 0: 
            for client in clients:
                if not client.handler.is_alive():
                    print(f"[!] Client '{client.username}' disconnected.")
                    clients.remove(client)
                    connections[0] -= 1
        sleep(1)

def chat():
    server = s.socket(s.AF_INET, s.SOCK_STREAM)
    server.bind(("127.0.0.1", 5432))
    server.listen(10)
    
    startup = [True]
    connections = [0]
    clients = []

    accepter = Thread(target=accept_clients, args=(server, clients, connections, startup))
    accepter.name = "accepter"
    accepter.start()
    
    heartbeat_thread = Thread(target=heartbeat, args=(clients, connections))
    heartbeat_thread.name = "heartbeat"
    heartbeat_thread.start()
        
    while True:
        if len(clients) == 0 and not startup[0]:
            print("No more clients connected, closing...")
            break
    
    server.close()

def game():
    pass

def main():
    print("---| Server Selector |---\n1. Chat\n2. Game")
    
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