import functools
import json
import flask
from flask import request, Response
from connection_handler import connection_handler

# Create blueprint
bp = flask.Blueprint('control', __name__, url_prefix='/control')

@bp.route('/set_baud', methods=["POST"])
def set_baud():
    data = request.json
    baud = int( data['baud'] )
    connection_handler.set_baud(baud)
    return Response("Baud rate was set", status=201, mimetype='application/json')

@bp.route('/set_port', methods=["POST"])
def set_port():
    data = request.json
    port = data['port']
    connection_handler.set_port(port)
    return Response("Port was set", status=201, mimetype='application/json')

@bp.route('/set_config', methods=["POST"])
def set_config():
    data = request.json
    config = data['file']
    connection_handler.set_config(config)
    return Response("Config was set", status=201, mimetype='application/json')

@bp.route('/connect', methods=["POST"])
def connect():
    res = connection_handler.connect()
    print(res)
    if res:
        return Response("Sucessfully connected", status=201, mimetype='application/json')
    else:
        return Response("Connection failed!", status=505, mimetype='application/json')

@bp.route('/get_ports', methods=["POST"])
def get_ports():
    return {'ports': connection_handler.get_ports() }
