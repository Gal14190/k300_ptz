import socket
import threading
import json
import time


class ApiDataHandler:
    def __init__(self, port):
        self.port = port
        self.data = {}
        self.data_lock = threading.Lock()
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.running = True

        self.server_thread.start()

    def handle_client(self, client_socket, client_address):
        print(f"Accepted connection from {client_address}")
        while self.running:
            data = client_socket.recv(1024)
            if not data:
                break
            try:
                received_data = json.loads(data.decode('utf-8'))
                source = received_data.get("source", "Unknown")
                with self.data_lock:
                    self.data[source] = received_data
                    # print(f"Received data from {source}: {self.data[source]}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
        client_socket.close()

    def start_server(self):
        PORT = self.port
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.listen(1)
        print(f"Server is listening on port {PORT}")

        while self.running:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

        server_socket.close()

    def stop_server(self):
        self.running = False
        print("Server has stopped")

    def get_data(self, source):
        with self.data_lock:
            return self.data.get(source, "No Data For Current Source Name")

    def wait_for_response(self, source, timeout=None):
        start_time = time.time()
        data = None

        while not data and (timeout is None or (time.time() - start_time) < timeout):
            data = self.get_data(source)
            if not data:
                time.sleep(0.1)
        return data


# def main():
#     api = ApiDataHandler(5678)
#     try:
#         while True:
#             panter = api.get_data("PANTER")
#             time.sleep(0.3)
#             if panter:
#                 print(panter)

#         input("Press Enter to stop the server...")
#     except KeyboardInterrupt:
#         pass
#     finally:
#         api.stop_server()
#         api.server_thread.join()


# if __name__ == "__main__":
#     main()
