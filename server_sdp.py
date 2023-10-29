import socket
import threading
import json
import time


class ApiLocations:
    def __init__(self, port):
        self.port = port
        self.yolo_data = None
        self.sdr_data = None
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True

        self.server_thread.start()
        self.yolo_data_condition = threading.Condition()
        self.sdr_data_condition = threading.Condition()
        self.yolo_data_lock = threading.Lock()
        self.sdr_data_lock = threading.Lock()

    def handle_client(self, client_socket, client_address):
        print(f"Accepted connection from {client_address}")
        while self.running:
            data = client_socket.recv(1024)
            if not data:
                break
            try:
                received_data = json.loads(data.decode('utf-8'))
                if received_data["source"] == "YOLO":
                    with self.yolo_data_lock:
                        self.yolo_data = received_data
                        print(self.yolo_data)
                elif received_data["source"] == "SDR":
                    with self.sdr_data_lock:
                        self.sdr_data = received_data
                        print(self.sdr_data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
        client_socket.close()

    def start_server(self):
        PORT = self.port
        self.running = True
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

    def getSDR_data(self):
        with self.sdr_data_lock:
            return self.sdr_data

    def getYOLO_data(self):
        with self.yolo_data_lock:
            return self.yolo_data

    def wait_for_response(self, source, timeout=None):
        start_time = time.time()
        data = None
        condition = self.yolo_data_condition if source == "YOLO" else self.sdr_data_condition

        with condition:
            while not data and (timeout is None or (time.time() - start_time) < timeout):
                condition.wait(timeout)
                if source == "YOLO":
                    data = self.getYOLO_data()
                elif source == "SDR":
                    data = self.getSDR_data()
            return data


# def main():

#     api = ApiLocations(5678)
#     try:

#         while True:
#             yolo_data = api.wait_for_response("YOLO", timeout=2)
#             sdr_data = api.wait_for_response("SDR", timeout=2)

#         input("Press Enter to stop the server...")
#     except KeyboardInterrupt:
#         pass
#     finally:
#         api.stop_server()
#         api.server_thread.join()


# if __name__ == "__main__":
#     main()
