import queue
import socket
import signal
import picamera

# signal handling
stop_queue = queue.Queue()

def stop_server(signum, frame):
    print("exiting...")
    stop_queue.put(1)

signal.signal(signal.SIGINT, stop_server)
signal.signal(signal.SIGTERM, stop_server)

# initialise camera
camera = picamera.PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 30
print("camera initialised")

# initialise server
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)
print("server started listening")

try:
    while stop_queue.empty():
        connection = server_socket.accept()[0].makefile('wb')
        print("connection accepted")
        try:
            camera.start_recording(connection, format='h264', quality=30)
            while stop_queue.empty():
                camera.wait_recording(2)
        except (BrokenPipeError, ConnectionResetError):
            print("connection closed")
        finally:
            try:
                camera.stop_recording()
            except (BrokenPipeError, ConnectionResetError):
                pass

            try: 
                connection.close()
            except BrokenPipeError:
                pass

finally:
    server_socket.close()
