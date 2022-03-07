import time
import json

import numpy as np
import flask
from flask import request, Response

from .db import get_db
from .connection_handler import connection_handler as ch

# Create blueprint
bp = flask.Blueprint('measure', __name__, url_prefix='/measure')

def random_histogram(bins):
    y = np.zeros(len(bins))
    while True:
        idx = int( np.clip(np.random.normal(200, 50), 0, 399) )
        y[idx] += 1
        yield y

# === GLOBALS ===
FRAME_ID = 0
MEASURING = None

# ToT
TOT_GENERATOR = None
TOT_HIST = None

# Dosi
DOSI_GENERATOR = None
DOSI_HIST = None

# === COMMON ===
@bp.route('/new_measurement', methods=["POST"])
def new_measurement():
    db = get_db()
    data = request.json
    global FRAME_ID

    # Check if required data is provided
    if not all([key in data.keys() for key in ['config_id', 'user_id', 'mode', 'name']]):
        return Response("Required keys are missing", status=400, mimetype='application/json')

    try:
        db.execute(
            "INSERT INTO measurement (config_id, user_id, mode, name) VALUES (?, ?, ?, ?)", 
            (data['config_id'], data['user_id'], data['mode'], data['name']))
        db.commit()
    except db.IntegrityError as error:
        return Response(error, status=409, mimetype='application/json')

    meas_id = db.execute("SELECT last_insert_rowid() FROM measurement").fetchone()
    meas_id = list(dict(meas_id).values())[0]

    # Counter for current frame
    FRAME_ID = 0
    return Response(json.dumps({'meas_id': meas_id}), status=201, mimetype='application/json')

@bp.route('/get_meas_ids_names', methods=["GET"])
def get_meas_ids_names():
    db = get_db()

    if ('user_id' in request.args) and ('mode' in request.args):
        user_id = request.args.get('user_id', type=int)
        mode = request.args.get('mode', type=str)

        ret = db.execute(
            'SELECT id, name FROM measurement WHERE (user_id, mode) IS (?, ?)', (user_id, mode)).fetchall()
        ret = [dict(r) for r in ret]
        if not ret:
            return Response("No entries found", status=404, mimetype='application/json')
    else:
        return Response("user_id and mode are required", status=406, mimetype='application/json')
    return Response(json.dumps(ret), status=201, mimetype='application/json')

# === MEASURE ToT ===
@bp.route('/tot', methods=["POST", "GET", "DELETE"])
def measure_tot():
    db = get_db()
    bins = np.arange(400)
    global FRAME_ID
    global TOT_GENERATOR
    global TOT_HIST

    # Start measurement
    if request.method == "GET":
        FRAME_ID = 0
        TOT_GENERATOR = ch.dpx.measureToT(slot=1, use_gui=True)
        TOT_HIST = np.zeros((256, 400))
        # hist_gen = random_histogram(np.arange(400))   # Debug
        return Response("Measurement started", status=201, mimetype='application/json')

    # Get events
    small_pixels = np.asarray([True if pixel % 16 in [0, 1, 14, 15] else False for pixel in np.arange(256)])
    if request.method == "POST":
        if TOT_GENERATOR is not None:
            # TODO
            # save = request.args.get('save', type=str)
            # If true, save ToT values to db
            frame = np.asarray( next( TOT_GENERATOR ) )

            # Get rid of zeros and large values
            frame_filt = np.array(frame, copy=True)
            frame_filt[frame_filt > bins[-1]] = 0

            pixel_hits = np.argwhere(frame_filt > 0).flatten()
            for px in pixel_hits:
                TOT_HIST[px][frame_filt[px]] += 1

            if 'show' in request.json.keys():
                show = request.json['show']
                if show == "large":
                    hist_show = np.sum(TOT_HIST[~small_pixels], axis=0).tolist()
                elif show == "small":
                    hist_show = np.sum(TOT_HIST[small_pixels], axis=0).tolist()
                # Show single pixels
                elif show == "single":
                    # If no pixels were selected, return empty
                    if not request.json['pixels']:
                        return Response(json.dumps({'bins': bins.tolist(), 'frame': np.zeros(400).tolist()}), status=200, mimetype='application/json')
                    hist_show = np.sum(TOT_HIST[np.asarray(request.json['pixels'])], axis=0).tolist()
                else:
                    hist_show = np.sum(TOT_HIST, axis=0).tolist()
            else:
                hist_show = np.sum(TOT_HIST, axis=0).tolist()

            # Store in database
            if request.json['mode'] != 'tot_hist':
                insert_list = []
                for idx in np.argwhere(frame > 0).flatten():
                    insert_list.append( (request.json['meas_id'], FRAME_ID, idx.item(), frame[idx].item()) )
                db.executemany("INSERT INTO totmode (measurement_id, frame_id, pixel_id, value) VALUES (?, ?, ?, ?)", insert_list)
                db.commit()
                FRAME_ID += 1

            # Return histogram
            return Response(json.dumps({'bins': bins.tolist(), 'frame': hist_show}), status=200, mimetype='application/json')
        return Response("Measurement not started", status=405, mimetype='application/json')

    # Stop measurement
    if request.method == "DELETE":
        if TOT_GENERATOR is not None:
            try:
                TOT_GENERATOR.close()
                TOT_GENERATOR = None
            except:
                TOT_GENERATOR = None

        meas_id = request.args.get('meas_id', type=int)
        if TOT_HIST is not None:
            res = save_tot_hist(bins, TOT_HIST, meas_id)
            if not res:
                return Response("Failed to store ToT histogram to db", status=500, mimetype='application/json')

        TOT_HIST = None
        return Response("Measurement stopped", status=201, mimetype='application/json')

def save_tot_hist(bins, hist, meas_id):
    db = get_db()

    try:
        # Loop over all pixels
        for pixel_id, h in enumerate( hist ):
            # Store in database

            insert_list = np.dstack( [[meas_id]*len(bins), [pixel_id]*len(bins), bins, h] )[0]
            db.executemany("INSERT INTO totmode_hist (measurement_id, pixel_id, bin, value) VALUES (?, ?, ?, ?)", insert_list)
            db.commit()
    except:
        return False
    return True

@bp.route('/tot_hist', methods=["GET"])
def tot_hist():
    db = get_db()

    if request.method == "GET":
        meas_id = request.args.get('meas_id', type=int)
        pixel_id = request.args.get('pixel_id', type=int)

        data = db.execute(
            'SELECT * FROM totmode_hist WHERE (measurement_id, pixel_id) IS (?, ?)', (meas_id, pixel_id)
        ).fetchall()
        data = json.dumps( [dict(d) for d in data] )
        return Response(data, status=200, mimetype='application/json')
    return Response("Bad ToT histogram request", status=400, mimetype='application/json')

# === MEASURE DOSI ===
@bp.route('/dosi', methods=["POST", "GET", "DELETE"])
def measure_dosi():
    db = get_db()
    bins = np.arange(400)
    global FRAME_ID
    global DOSI_GENERATOR
    global DOSI_HIST

    # Start measurement
    if request.method == "GET":
        FRAME_ID = 0
        frames = request.args.get('frames', default=-1, type=int)
        frame_time = request.args.get('frame_time', default=10, type=int)

        # Infinite measurement
        if frames <= 0:
            frames = None
        DOSI_GENERATOR = ch.dpx.measureDose(slot=1, frame_time=frame_time, frames=frames, 
                                            freq=False, outFn=None, logTemp=False, intPlot=False, 
                                            conversion_factors=None, use_gui=False)
        DOSI_HIST = []
        return Response("Measurement started", status=201, mimetype='application/json')

    # Get events
    small_pixels = np.asarray([True if pixel % 16 in [0, 1, 14, 15] else False for pixel in np.arange(256)])
    if request.method == "POST":
        if DOSI_GENERATOR is not None:
            frame = np.asarray( next( DOSI_GENERATOR ) )
            DOSI_HIST.append( frame )
            print( frame )

            if 'show' in request.json.keys():
                show = request.json['show']
                if show == "large":
                    hist_show = np.sum(DOSI_HIST, axis=0)[~small_pixels].tolist()
                elif show == "small":
                    hist_show = np.sum(DOSI_HIST, axis=0)[small_pixels].tolist()
                # Show single pixels
                elif show == "single":
                    # If no pixels were selected, return empty
                    if not request.json['pixels']:
                        return Response(json.dumps({}), status=200, mimetype='application/json')
                    hist_show = np.sum(DOSI_HIST, axis=0)[np.asarray(request.json['pixels'])].tolist()
                else:
                    hist_show = np.sum(DOSI_HIST, axis=0).tolist()
            else:
                hist_show = np.sum(DOSI_HIST, axis=0).tolist()

            # Store in database
            if request.json['mode'] == 'dosi':
                db.execute("INSERT INTO dosimode (measurement_id, frame_id, %s) VALUES (%s)" % (', '.join(['bin%d' % b for b in range(16)]), ', '.join(['?'] * 18)), [request.json['meas_id'], FRAME_ID] + np.sum(frame, axis=0).tolist())
                db.commit()
                FRAME_ID += 1

            # Return histogram
            return Response(json.dumps({'bins': bins.tolist(), 'frame': hist_show}), status=200, mimetype='application/json')
        return Response("Measurement not started", status=405, mimetype='application/json')

    # Stop measurement
    if request.method == "DELETE":
        if DOSI_GENERATOR is not None:
            try:
                DOSI_GENERATOR.close()
                DOSI_GENERATOR = None
            except:
                DOSI_GENERATOR = None
        return Response("Measurement stopped", status=201, mimetype='application/json')

# === THL CALIBRATION ===
@bp.route('/thl_calib', methods=["POST", "GET", "DELETE"])
def thl_calib():
    db = get_db()
    global GENERATOR

    if request.method == "GET":
        GENERATOR = ch.dpx.measureADC(1, AnalogOut='V_ThA', perc=False, ADChigh=8191, ADClow=0, ADCstep=1, N=1, fn=None, plot=False, use_gui=True)
        return Response("Calibration started", status=201, mimetype='application/json')

    if request.method == "POST":
        if GENERATOR is not None:
            try:
                res = next( GENERATOR )
            except StopIteration:
                return Response('finished', status=410, mimetype='application/json')
            return Response(json.dumps(res), status=201, mimetype='application/json')

    if request.method == "DELETE":
        if GENERATOR is not None:
            try:
                GENERATOR.close()
            except:
                GENERATOR = None
        return Response("THL Calibration stopped", status=201, mimetype='application/json')

# === EQUALIZATION ===
@bp.route('/equal', methods=["POST", "GET", "DELETE"])
def equalization():
    db = get_db()
    global GENERATOR

    # Create equalization generator
    if request.method == "GET":
        GENERATOR = ch.dpx.thresholdEqualization(slot=1, reps=1, THL_offset=20, I_pixeldac=None, intPlot=False, resPlot=False, use_gui=True)
        return Response("Equalization started", status=201, mimetype='application/json')

    if request.method == "POST":
        if GENERATOR is not None:
            try:
                res = next( GENERATOR )
                print( res )
            except StopIteration as excp:
                return Response(json.dumps(excp.value), status=200, mimetype='application/json')
            return Response(json.dumps(res), status=201, mimetype='application/json')

    if request.method == "DELETE":
        if GENERATOR is not None:
            try:
                GENERATOR.close()
            except:
                GENERATOR = None
        return Response("Equalization stopped", status=201, mimetype='application/json')
