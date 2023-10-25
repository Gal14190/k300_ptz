import socket
import threading
import json

class ApiLocations:
    def __init__(self, port):
        self.port = port
        self.sending_data = None
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def start_server(self):
        PORT = self.port
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.listen(1)
        print(f"Server is listening on port {PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            data = client_socket.recv(1024)
            try:
                received_data = json.loads(data.decode('utf-8'))  
                keys_to_extract = ["latitude", "longitude", "altitude"]
                self.sending_data = {key: received_data.get(key, None) for key in keys_to_extract}
                # print(f"Received: {self.sending_data}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

            client_socket.sendall(b'Message received by the server')
            client_socket.close()

    def location_details(self):
        return self.sending_data

# def main():
#     api = ApiLocations()
#     api.location_details()
#     print("check Thread")
#     while True:
#         pass

# if __name__ == "__main__":
#     main()

