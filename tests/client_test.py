import socketio

sio = socketio.Client()


@sio.event
def connect():
    print("Connection established")
    sio.emit(
        "send_message", {"recipient": "user2", "message": "Hello from user1!"}
    )


@sio.event
def disconnect():
    print("Disconnected from server")


@sio.on("user_connected")
def on_user_connected(data):
    print(f"User connected: {data['username']}")


@sio.on("user_disconnected")
def on_user_disconnected(data):
    print(f"User disconnected: {data['username']}")


@sio.on("update_user_list")
def on_update_user_list(data):
    print(f"Connected users: {', '.join(data)}")


@sio.on("receive_message")
def on_receive_message(data):
    print(f"Received message from {data['sender']}: {data['message']}")


if __name__ == "__main__":
    username = "user2"  # Change this for different clients
    sio.connect(
        "http://localhost:5000",
        transports="websocket",
        headers={"username": username},
    )
    sio.wait()
