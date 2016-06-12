"""

The API.

Sits in the background managing things :)

"""
from genghisio import app
from genghisio import socketio

import flask
import genghisio.api.backend
import genghisio.drivers
import genghisio.controlqueue
import genghisio.store
import os


@socketio.on('ping', namespace='/api')
def ping(data):
    """ Repeat a ping from the bot to the front-end.

    The ping contains the sessionId, which we use to join that sessionId's
    room - this ensures the message we send only goes to the front-end for
    that room. The ping also contains the state of the sensors on the bot and
    a blacklist of methods not to call, we on send that to the font-end.

    """
    room = data['sessionId']

    # Create a blacklist of behaviours that have queued controls already
    blacklist = genghisio.api.backend.blacklist(
        genghisio.store.get_controls(room))

    # Join the room to target the emit()
    flask.ext.socketio.join_room(room)

    # Send the emit()
    flask.ext.socketio.emit('ping', {
        'inputs': data['inputs'],
        'botId': data['botId'],
        'blacklist': blacklist,
    }, room=room)


@socketio.on('control', namespace='/api')
def control(data):
    """ Repeat a ping from the front-end to the bot.

    The ping contains the sessionId, which we use to ensure the message we
    send only goes to the bot's room. The ping also contains the latest
    controls from the code, which we we push into a queue, then send the head
    to the bot.

    """
    # The room is used to target the send to the bot, and to filter control
    # queues in memcached.
    room = data['sessionId']

    # Update the queue and return a new queue, head and any debug messages
    new_queue, head, debug = genghisio.api.backend.queue_step(
        genghisio.store.get_controls(room),
        data['controls'],
        data['behaviours'])

    # Save the updated queued controls
    genghisio.store.set_controls(room, new_queue)

    # Send off any debug messages
    for message in debug:
        flask.ext.socketio.emit('debug', {
            'msg': message,
        }, room=room)

    # Return if no controls to send
    if head is None:
        return

    # Send the serial string for the control to the bot
    flask.ext.socketio.emit('control', {
        'control': genghisio.api.backend.get_output(data['botId'], *head[:2]),
    }, room=room)


@socketio.on('register', namespace='/api')
def register(data):
    """ Handle PC browser registrations.

    The register call is executed by the front-end when it has a valid
    sessionId to register with. As the front-end only responds to pings (to
    trigger the execution of Python code), it has to tell the server that it
    is in the same room as it's sessionId (which is the room the bot will use
    to send the ping from and to).

    """
    room = data['sessionId']
    flask.ext.socketio.join_room(room)


@app.route('/api/file', methods=['POST'])
def upload_file():
    """ Handle submitting Python source via uploading a file.

    The returned source is formatted for execution.

    """
    file = flask.request.files['file']
    if not file:
        return ''

    # Store the file in RAM so we can send it back to the user via a
    # websocket. TODO: This needs to be thought about carefully so we don't
    # run out of RAM/get DoS'd.
    contents = file.stream.read(app.config['MAX_CONTENT_LENGTH'])

    # Format the submitted code
    src = genghisio.api.backend.format_file(
        contents,
        app.open_resource('templates/header.py').read(),
        app.open_resource('templates/footer.py').read()
    )

    # Send it to the user via websockets
    room = flask.request.form['sessionId']
    socketio.emit('code', {
        'src': src,
        'filename': os.path.basename(file.filename),
        'sessionId': room,
    }, room=room, namespace='/api')

    # And we're done
    return ''


@app.route('/api/sid')
def new_session_id():
    """ Returns a new session id in JSON.
    """
    return flask.jsonify({
        'sessionId': genghisio.api.backend.new_sid()
    })
