import functools
import json
import flask
from flask import request, Response
from .db import get_db

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
    except db.IntegrityError:
        error = "Config %s already registered" % data['name']
        flask.flash(error)
        return Response(error, status=409, mimetype='application/json')

    return Response("New user was created", status=201, mimetype='application/json')

@bp.route('/get_all', methods=["GET"])
def get_configs():
    db = get_db()

    configs = db.execute(
        'SELECT * FROM config',
    ).fetchall()
    configs = json.dumps( [dict(config) for config in configs] )

    return Response(configs, status=200, mimetype='application/json')

@bp.route('/new_thl_calib', methods=["POST"])
def new_thl_calib():
    db = get_db()
    data = request.json
    print(data)

    # Check if required data is provided
    if not all([key in ['volt', 'ADC'] for key in data.keys()]):
        return Response("Required keys are missing", status=400, mimetype='application/json')

        
