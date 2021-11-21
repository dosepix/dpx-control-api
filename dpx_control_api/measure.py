import numpy as np
import time
import functools
import json
import flask
from flask import request, Response
from .db import get_db

# Create blueprint
bp = flask.Blueprint('measure', __name__, url_prefix='/measure')

def random_histogram(bins):
    y = np.zeros(len(bins))
    while True:
        idx = int( np.clip(np.random.normal(30, 10), 0, 99) )
        y[idx] += 1
        yield y

hist_gen = None
MEASURING = False
@bp.route('/tot', methods=["POST", "GET", "DELETE"])
def measure_tot():
    print(request.method)
    db = get_db()
    global hist_gen

    # Start measurement
    if request.method == "POST":
        hist_gen = random_histogram(np.arange(100))
        return Response("Measurement started", status=201, mimetype='application/json')

    # Get events
    if request.method == "GET":
        if hist_gen is not None:
            num_frames = 10 # request.json['frames']
            frames = []
            for frame in range(num_frames):
                frames.append( next( hist_gen ).tolist() )
                time.sleep(1. / 17)
            
            return Response(json.dumps({'bins': np.arange(100).tolist(), 'frame': frames[-1]}), status=200, mimetype='application/json')
        return Response("Measurement not started", status=405, mimetype='application/json')

    # Stop measurement
    if request.method == "DELETE":
        if hist_gen is not None:
            hist_gen.close()
        return Response("Measurement stopped", status=201, mimetype='application/json')
