import functools
import json
import flask
from flask import request, Response
from .db import get_db

# Create blueprint
bp = flask.Blueprint('user', __name__, url_prefix='/user')

@bp.route('/new_user', methods=["POST"])
def new_user():
    db = get_db()
    data = request.json
    name = data['name']

    if not name:
        error = "Username is required"
        flask.flash(error)
        return

    try:
        db.execute(
            "INSERT INTO user (name) VALUES (?)",
            (name, ),
        )
        db.commit()
    except db.IntegrityError:
        error = "User {name} already registered"
        flask.flash(error)
        return Response(error, status=405, mimetype='application/json')

    return Response("New user was created", status=201, mimetype='application/json')

@bp.route('/get_users', methods=["GET"])
def get_users():
    db = get_db()

    users = db.execute(
        'SELECT * FROM user',
    ).fetchall()
    users = json.dumps( [dict(user) for user in users] )

    return Response(users, status=200, mimetype='application/json')
