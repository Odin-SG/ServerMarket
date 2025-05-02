from flask_socketio import join_room, emit
from flask_login import current_user
from app import socketio, db
from app.models.chat_message import ChatMessage
from datetime import datetime

@socketio.on('join')
def on_join(data):
    order_id = data.get('order_id')
    room = f'order_{order_id}'
    join_room(room)

@socketio.on('send_chat')
def on_send_chat(data):
    order_id = data.get('order_id')
    text = data.get('message', '').strip()
    if not text:
        return

    msg = ChatMessage(
        order_id=order_id,
        user_id=current_user.id,
        message=text,
        created_at=datetime.utcnow()
    )
    db.session.add(msg)
    db.session.commit()

    room = f'order_{order_id}'
    emit('receive_chat', {
        'username': current_user.username,
        'message': text,
        'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M')
    }, room=room)
