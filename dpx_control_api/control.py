import flask
from flask import g, current_app, request, Response

from .connection_handler import connection_handler as ch

# Create blueprint
bp = flask.Blueprint('control', __name__, url_prefix='/control')

@bp.route('/set_baud', methods=["POST"])
def set_baud():
    data = request.json
    baud = int( data['baud'] )
    ch.set_baud(baud)
    return Response("Baud rate was set", status=201, mimetype='application/json')

@bp.route('/set_port', methods=["POST"])
def set_port():
    data = request.json
    port = data['port']
    ch.set_port(port)
    return Response("Port was set", status=201, mimetype='application/json')

@bp.route('/set_config', methods=["POST"])
def set_config():
    data = request.json
    config = data['file']
    ch.set_config(config)
    return Response("Config was set", status=201, mimetype='application/json')

@bp.route('/connect', methods=["POST", "DELETE"])
def connect():
    print(request.method)
    # Establish new connection
    if request.method == "POST":
        if ch.is_connected():
            return Response("Already connected", status=412, mimetype='application/json')

        res = ch.connect()
        if res & (res == 503):
            return Response("Permission denied", status=503, mimetype='application/json')
        elif res & (res == 400):
            return Response("Baud rate or port missing", status=400, mimetype='application/json')
        elif res:
            return Response("Successfully connected", status=201, mimetype='application/json')
        else:
            return Response("Connection failed", status=505, mimetype='application/json')
    # Disconnect
    elif request.method == "DELETE":
        try:
            if ch.is_connected():
                res = ch.disconnect()
                return Response("Device disconnected", status=201, mimetype='application/json')
            else:
                return Response("No device connected", status=412, mimetype='application/json')
        except:
            ch.dpx = None
            return Response("Disonnect failed, forced disconnect", status=500, mimetype='application/json')

@bp.route('/isconnected', methods=["GET"])
def isconnected():
    res = ch.is_connected()
    if res:
        return Response("Device connected", status=201, mimetype='application/json')
    else:
        return Response("Device not connected", status=404, mimetype='application/json')

@bp.route('/get_ports', methods=["POST"])
def get_ports():
    return {'ports': ch.get_ports() }
