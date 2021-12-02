import functools
import json
import flask
from flask import request, Response
from .db import get_db

from connection_handler import connection_handler as ch

# Create blueprint
bp = flask.Blueprint('config', __name__, url_prefix='/config')

@bp.route('/new', methods=["POST"])
def new_config():
    db = get_db()
    data = request.json

    required_keys = ["name", "dosepix_id", "user_id", "i_krum"]
    advanced_keys = ["v_casc_preamp", "v_casc_reset", "i_pixeldac", "i_tpbufin", "v_tpref_fine", "v_gnd", "i_disc2", "i_disc1", "i_preamp", "v_tha", "v_tpref_coarse", "i_tpbufout", "v_fbk"]
    equal_keys = ["confbits", "pixeldac"]

    # Some parameters are required
    if not set(required_keys).issubset(set(data.keys())):
        print(data)
        return Response('Required values are missing', status=400, mimetype='application/json')

    # Build lists of values and keys
    keys = required_keys

    for key in advanced_keys:
        if key in data.keys():
            keys.append( [key] )

    for key in equal_keys:
        if key in data.keys():
            keys.append( [key] )

    values = [data[key] for key in keys]

    print(keys)
    print(values)

    try:
        db.execute(
            "INSERT INTO config (%s) VALUES (%s)" % (', '.join(keys), ', '.join(['?'] * len(keys))),
            values,
        )
        db.commit()
        # Get id of created config
        config_id = db.execute("SELECT last_insert_rowid() FROM config").fetchone()
        config_id = list(dict(config_id).values())[0]
    except db.IntegrityError:
        error = "Config %s already registered" % data['name']
        flask.flash(error)
        return Response(error, status=409, mimetype='application/json')

    return Response(json.dumps({'config_id': config_id}), status=201, mimetype='application/json')

@bp.route('/get', methods=["GET"])
def get_config():
    db = get_db()
    # Get parameters
    id = request.args.get('id', default=-1, type=int)
    if id < 0:
        return Response('No parameter provided', status=400, mimetype='application/json')

    config = db.execute(
        'SELECT id, name FROM config WHERE id=%d' % id,).fetchone()
    if not config:
        return Response('Config not found', status=404, mimetype='application/json')

    config = dict(config)
    return Response(json.dumps(config), status=200, mimetype='application/json')

@bp.route('/get_all', methods=["GET"])
def get_configs():
    db = get_db()

    if 'dpx_id' in request.args:
        dpx_id = request.args.get('dpx_id', default=-1, type=int)
        # If parameter provided
        configs = db.execute(
            'SELECT id, name FROM config WHERE dosepix_id=%d' % dpx_id,
        ).fetchall()
    else:
        configs = db.execute(
            'SELECT id, name FROM config',
        ).fetchall()
    if not configs:
        return Response('No configs found', status=404, mimetype='application/json')
    configs = json.dumps( [dict(config) for config in configs] )
    return Response(configs, status=200, mimetype='application/json')

@bp.route('/new_thl_calib', methods=["POST"])
def new_thl_calib():
    db = get_db()
    data = request.json
    print(data)

    # Check if required data is provided
    if not all([key in data.keys() for key in ['config_id', 'name', 'volt', 'ADC']]):
        return Response("Required keys are missing", status=400, mimetype='application/json')

    config_id, name = data['config_id'], data['name']
    # Insert THL Calib if not already existing
    try:
        db.execute("INSERT INTO thl_calib (name, config_id) VALUES (?, ?)", (name, config_id,))
        db.commit()

        # Get id
        thl_calib_id = db.execute("SELECT last_insert_rowid() FROM thl_calib").fetchone()
        thl_calib_id = list(dict(thl_calib_id).values())[0]
    except db.IntegrityError:
        error = "THL Calib %s already registered" % data['name']
        flask.flash(error)
        return Response(error, status=409, mimetype='application/json')

    volt, ADC = data['volt'], data['ADC']
    if len(volt) != len(ADC):
        return Response("Shape mismatch", status=406, mimetype='application/json')

    try:
        for idx in range(len(volt)):
            db.execute(
                "INSERT INTO thl_calib_data (thl_calib_id, volt, ADC) VALUES (?, ?, ?)", (thl_calib_id, volt[idx], ADC[idx]),
            )
            db.commit()

    except db.IntegrityError:
        # If failed, delete last row
        db.execute("DELETE FROM thl_calib WHERE id = (?)", thl_calib_id,)
        db.commit()

        error = "Error writing THL Calib %s" % data['name']
        flask.flash(error)
        return Response(error, status=409, mimetype='application/json')

    return Response(json.dumps({'thl_calib_id': thl_calib_id}), status=201, mimetype='application/json')

def get_thl_calib_from_id(thl_calib_id):
    db = get_db()

    # Query data
    data = db.execute(
        'SELECT ADC, volt FROM thl_calib_data WHERE (thl_calib_id) IS (?)', (thl_calib_id,)).fetchall()

    # Package data and return
    volt = [d['volt'] for d in data]
    ADC = [d['ADC'] for d in data]

    return {'Volt': volt, 'ADC': ADC}

@bp.route('/get_thl_calib_ids_names', methods=["GET"])
def get_thl_calib_ids_names():
    db = get_db()

    if 'config_id' in request.args:
        config_id = request.args.get('config_id', type=int)
        ret = db.execute(
            'SELECT id, name FROM thl_calib WHERE (config_id) IS (?)', (config_id,)).fetchall()
        ret = [dict(r) for r in ret]
        if not ret:
            return Response("No entries found", status=404, mimetype='application/json')
    else:
        return Response("config_id is required", status=406, mimetype='application/json')
    return Response(json.dumps(ret), status=201, mimetype='application/json')

@bp.route('/get_thl_calib', methods=["GET"])
def get_thl_calib():
    if 'thl_calib_id' in request.args:
        thl_calib_id = request.args.get('thl_calib_id', default=-1, type=int)
        ret = get_thl_calib_from_id(thl_calib_id)

        if not ret['Volt']:
            return Response("No data found", status=400, mimetype='application/json')
    else:
        return Response("thl_calib_id is required", status=406, mimetype='application/json')
    return Response(json.dumps(ret), status=201, mimetype='application/json')

@bp.route('/get_thl_calib_id', methods=["GET"])
def get_thl_calib_id():
    db = get_db()
    if ('config_id' in request.args) and ('name' in request.args):
        config_id = request.args.get('config_id', type=int)
        name = request.args.get('name', type=str)
        ret = db.execute(
            'SELECT id FROM thl_calib WHERE (config_id, name) IS (?, ?)', (name,)).fetchone()
        ret = dict(ret)
        if not ret:
            return Response("Id not found", status=404, mimetype='application/json')
        return Response(json.dumps({'thl_calib_id': ret}), status=201, mimetype='application/json')
    else:
        return Response('Required parameters are missing', status=400, mimetype='application/json')

# Set THL calibration to Dosepix
@bp.route('/set_thl_calib', methods=["GET"])
def set_thl_calib():
    thl_calib_id = request.args.get('id', default=-1, type=int)
    ret = get_thl_calib_from_id(thl_calib_id)
    print(thl_calib_id)
    print(ret)

    # Check if query results in data
    if not ret['Volt']:
        return Response("No data found", status=400, mimetype='application/json')
    
    # Check if device is connected
    if not ch.is_connected():
        return Response("No device connected", status=404, mimetype='application/json')

    # Set THL edges of DPX
    ch.dpx.load_THLEdges(ret)
    return Response("Succesfully set THL calibration", status=201, mimetype='application/json')
