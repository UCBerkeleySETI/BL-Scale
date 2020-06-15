import functools

from flask import (
    Blueprint, render_template
)

bp = Blueprint('monitor', __name__, url_prefix='/monitor')


@bp.route('/')
def base():
    return render_template("monitor.html", title="Monitor")
