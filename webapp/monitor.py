import functools

from flask import (
    Blueprint, render_template
)

bp = Blueprint('monitor', __name__, url_prefix='/monitor')


@bp.route('/<uid>')
def base(uid=None):
    return render_template("monitor.html", title="Monitor", uid=uid)
