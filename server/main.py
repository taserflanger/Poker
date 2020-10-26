import socketio
import eventlet

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})


@sio.on('connect')
def connect(sid, e):
    print('client connecté')


@sio.on('msg')
def msg(sid, m):
    print(m)


@sio.on('disconnect')
def disconnect(sid):
    print('client déconnecté')


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
