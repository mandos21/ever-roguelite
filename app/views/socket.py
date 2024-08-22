from flask_socketio import emit

from app import socketio
from app.models.user import User
from app.utils.auth_utils import token_required


@socketio.on('connect', namespace='/socket')
@token_required()
def handle_connect(current_user, **kwargs):
    username = current_user.username
    emit('system_message', {'msg': f'{username} has connected.'}, broadcast=True)


@socketio.on('disconnect', namespace='/socket')
@token_required()
def handle_disconnect(current_user, **kwargs):
    username = current_user.username
    emit('system_message', {'msg': f'{username} has disconnected.'}, broadcast=True)


@socketio.on('system_message', namespace='/socket')
@token_required()
def handle_system_message(data, **kwargs):
    message = data.get('message')
    if message:
        emit('system_message', {'msg': f'{kwargs["current_user"].username}: {message}'}, broadcast=True)


@socketio.on('dm_message', namespace='/socket')
@token_required(dm_required=True)
def handle_dm_message(data, **kwargs):
    user_ids = data.get('user_ids', [])
    message = data.get('message')

    if not message:
        return

    if user_ids:
        # Send the message to specific users
        for uid in user_ids:
            user = User.objects(_id=uid).first()
            if user:
                emit('dm_message', {'msg': message}, to=user.uid)
    else:
        # Broadcast the message to everyone
        emit('dm_message', {'msg': message}, broadcast=True)
