import socketio

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
app = socketio.ASGIApp(sio)


@sio.on('connect')
def connect(sid, e):
    print('client connecté')


@sio.on('msg')
def msg(sid, m):
    print(m)


@sio.on('disconnect')
def disconnect(sid):
    print('client déconnecté')
