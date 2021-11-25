import numpy as np
import time
import functools
import json
import flask
from flask import request, Response
from .db import get_db

from connection_handler import connection_handler as ch

# Create blueprint
bp = flask.Blueprint('measure', __name__, url_prefix='/measure')

def random_histogram(bins):
    y = np.zeros(len(bins))
    while True:
        idx = int( np.clip(np.random.normal(200, 50), 0, 399) )
        y[idx] += 1
        yield y

# === GLOBALS ===
GENERATOR = None
HIST = None
MEASURING = None

# === MEASURE ToT ===
@bp.route('/tot', methods=["POST", "GET", "DELETE"])
def measure_tot():
    db = get_db()
    global GENERATOR
    global HIST

    # Start measurement
    if request.method == "GET":
        GENERATOR = ch.dpx.measureToT(slot=1, use_gui=True)
        HIST = np.zeros((256, 400))
        # hist_gen = random_histogram(np.arange(400))   # Debug
        return Response("Measurement started", status=201, mimetype='application/json')

    # Get events
    small_pixels = np.asarray([True if pixel % 16 in [0, 1, 14, 15] else False for pixel in np.arange(256)])
    if request.method == "POST":
        bins = np.arange(400)
        if GENERATOR is not None:
            frame = np.asarray( next( GENERATOR ) )

            # Get rid of zeros and large values
            frame_filt = np.array(frame, copy=True)
            frame_filt[frame_filt > bins[-1]] = 0

            pixel_hits = np.argwhere(frame_filt > 0).flatten()
            for px in pixel_hits:
                HIST[px][frame_filt[px]] += 1

            if request.json is not None:
                show = request.json['show']
                if show == "large":
                    hist_show = np.sum(HIST[~small_pixels], axis=0).tolist()
                elif show == "small":
                    hist_show = np.sum(HIST[small_pixels], axis=0).tolist()
                elif show == "single":
                    if not request.json['pixels']:
                        return Response(json.dumps({'bins': bins.tolist(), 'frame': np.zeros(400).tolist()}), status=200, mimetype='application/json')
                    hist_show = np.sum(HIST[np.asarray(request.json['pixels'])]).tolist()
                else:
                    hist_show = np.sum(HIST, axis=0).tolist()
            else:
                hist_show = np.sum(HIST, axis=0).tolist()
            # hist_show = HIST[7].tolist()

            return Response(json.dumps({'bins': bins.tolist(), 'frame': hist_show}), status=200, mimetype='application/json')
        return Response("Measurement not started", status=405, mimetype='application/json')

    # Stop measurement
    if request.method == "DELETE":
        if GENERATOR is not None:
            try:
                GENERATOR.close()
            except:
                GENERATOR = None
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
            except StopIteration:
                return Response('finished', status=410, mimetype='application/json')
            return Response(json.dumps(res), status=201, mimetype='application/json')

    if request.method == "DELETE":
        if GENERATOR is not None:
            try:
                GENERATOR.close()
            except:
                GENERATOR = None
        return Response("Equalization stopped", status=201, mimetype='application/json')
