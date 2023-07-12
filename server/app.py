from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, join_room, leave_room, rooms
from flask_cors import CORS, cross_origin

from bs4 import BeautifulSoup
import requests

import json, string, random, time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173") # Allowed origins must be set
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})     # both for socjetio and flask-app


@socketio.on('join')
def on_join(data):
    join_room(data['room'])
    socketio.emit('user-joined', room=data['room'])


@socketio.on('client-close')
def on_leave(data):
    print('foo')
    socketio.emit('client-close', data)
    leave_room(data['room'])


@app.route('/client-close', methods=['POST'])
def client_close():
    print('foo')


@socketio.on('sync')
def sync(data):
    socketio.emit('sync', data, room=data['room'])


@socketio.on('sync-me')
def snyc_me(data):
    socketio.emit('sync-me', data, room=data['room'])


@socketio.on('play')
def play(data):
    socketio.emit('play', room=data['room'])


@socketio.on('pause')
def pause(data):
    socketio.emit('pause', room=data['room'])


@socketio.on('change-video')
def change_video(data):
    data['source'] = extract_video_src(data['source'])
    if data['source'] == 'error':
        socketio.emit('message', {'user': '', 'message': 'Invalid Link.'}, room=data['room'])
    socketio.emit('change-video', data,  room=data['room'])


@socketio.on('message')
def handle_message(data):
    socketio.emit('message', data, room=data['room'])


def extract_video_src(url):
    if not url:
        return 'error'

    url = url.replace('https://', '')
    url = url.replace('www.', '')
    url = url.replace('youtube.com/', '')
    
    try:
        response = requests.get(f"https://clipzag.com/{url}")

        soup = BeautifulSoup(response.content, 'html.parser')
        link = soup.find("a", {"class": "btn btn-primary btn-block p720"})

        return str(link['href']).replace('amp;', '')
    except Exception as e:
        return 'error'

        
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
