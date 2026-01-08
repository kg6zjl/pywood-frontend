from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os

# flask setuo
app = Flask(__name__)
# Configure Socket.IO with sane heartbeat timeouts so dead clients are cleaned up
socketio = SocketIO(
    app,
    ping_timeout=20,      # seconds to wait for a pong before disconnecting
    ping_interval=25,     # seconds between pings
    cors_allowed_origins="*"
)

# websocket bradcast settings
ROOM = "derbyrace"
NAMESPACE = "/"

# Configure logging to file with rotation
file_handler = RotatingFileHandler('logs/app.log', maxBytes=50000, backupCount=1)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

# send app logs to app logger
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

# send flask logs to app logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addHandler(file_handler)
werkzeug_logger.setLevel(logging.DEBUG)

# sqlite setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///race_results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# define our db schema
class RaceResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    lane = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    time_microseconds = db.Column(db.BigInteger, nullable=False, default=0)

    # Add a unique constraint so we don't write dupe data
    __table_args__ = (
        UniqueConstraint('race_id', 'lane', 'position', name='unique_race_lane_position'),
    )

# Create the database tables within the application context
with app.app_context():
    db.create_all()

    # Initialize the race ID
    def initialize_race_id():
        last_race = db.session.query(RaceResult.race_id).order_by(RaceResult.race_id.desc()).first()
        return (last_race[0] + 1) if last_race else 1

    current_race_id = initialize_race_id()

results = {}
active_clients = set()

# API endpoint
@app.route('/api/v1/results', methods=['POST'])
def post_results():
    global results
    data = request.json
    results = {position.lower(): str(lane) for position, lane in data.items()}
    for position, lane in data.items():
        try:
            race_result = RaceResult(race_id=current_race_id, lane=str(lane), position=position.lower())
            db.session.add(race_result)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            continue  # Skip the duplicate entry and move to the next
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
    # send to all ROOM clients
    emit('new_results', results, room=ROOM, namespace=NAMESPACE)
    app.logger.info(f"Results posted: {results}")
    return jsonify({'status': 'success'}), 201

# API endpoint
@app.route('/api/v1/reset', methods=['POST', 'PUT'])
def reset_results():
    global results, current_race_id
    results = {}
    current_race_id += 1
    # send to all ROOM clients
    emit('reset_results', room=ROOM, namespace=NAMESPACE)
    app.logger.info(f"RESET - Next Race ID: { current_race_id }")
    return jsonify({'status': 'results reset'}), 200

# html view
@app.route('/')
def serve_html():
    return send_from_directory(os.getcwd(), 'static/index.html')

@app.route('/static/<path:path>')
def static_proxy(path):
    return send_from_directory(f"{ os.getcwd() }/static", path)

@app.route('/results')
def view_results():
    results = db.session.query(
        RaceResult.race_id,
        func.group_concat(RaceResult.lane, ',').label('lanes'),
        func.group_concat(RaceResult.position, ',').label('positions')
    ).group_by(RaceResult.race_id).order_by(RaceResult.race_id.desc()).all()

    organized_results = []
    for result in results:
        lanes = result.lanes.split(',')
        positions = result.positions.split(',')
        result_dict = {"id": result.race_id, "first": "", "second": "", "third": "", "fourth": ""}
        for lane, position in zip(lanes, positions):
            result_dict[position] = lane
        organized_results.append(result_dict)
    
    return jsonify(organized_results)

@app.route('/results/<int:race_id>')
def view_single_result(race_id):
    result = db.session.query(
        RaceResult.race_id,
        RaceResult.date,
        func.group_concat(RaceResult.lane, ',').label('lanes'),
        func.group_concat(RaceResult.position, ',').label('positions')
    ).filter(RaceResult.race_id == race_id).group_by(RaceResult.race_id).first()

    if result:
        lanes = result.lanes.split(',')
        positions = result.positions.split(',')
        result_dict = {
            "id": result.race_id,
            "date": result.date.strftime('%Y-%m-%d %H:%M:%S'),
            "first": "",
            "second": "",
            "third": "",
            "fourth": ""
        }
        for lane, position in zip(lanes, positions):
            result_dict[position] = lane
        return jsonify(result_dict)
    else:
        return jsonify({"error": "Race ID not found"}), 404

@socketio.on('connect')
def test_connect():
    # Track active client sessions by sid
    try:
        active_clients.add(request.sid)
    except Exception:
        pass
    join_room(ROOM)
    # Send current race state to new client immediately
    if results:
        emit('new_results', results)
    app.logger.info(f"Client connected (active={len(active_clients)}), synced={bool(results)}")

@socketio.on('disconnect')
def test_disconnect():
    try:
        active_clients.discard(request.sid)
    except Exception:
        pass
    app.logger.info(f"Client disconnected (active={len(active_clients)})")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
