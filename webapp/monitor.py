import functools
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import base64
import io
from flask import (
    Blueprint, render_template
)

bp = Blueprint('monitor', __name__, url_prefix='/monitor')

def get_base64_hist(entry_cpu, entry_ram):
    time =10
    x = np.arange(time)
    y1=[]
    for i in range (10):
        y1.append(int(random.random()*100))
    y1.append(entry_cpu)
    if len(y1) >10:
        y1.pop(0)
    y2=[]
    for i in range (10):
        y2.append(int(random.random()*100))
    y2.append(entry_ram)
    if len(y2) >10:
        y2.pop(0)
    plt.style.use("dark_background")
    plt.figure(figsize=(8,6))
    plt.plot(x, y1)
    plt.plot(x, y2)
    plt.title("Health")
    plt.xlabel("Time")
    plt.ylabel("Percent % ")
    plt.legend(['CPU', 'MEMORY' ], loc='upper left')
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png')
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())
    base64_img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
    return base64_img
@bp.route('/')

def base():
    # get data from socket. 
    cpu_usage = 25
    ram_usage = 29
    image_encode = get_base64_hist(cpu_usage, ram_usage)
    return render_template("monitor.html", title="Monitor", encoded = image_encode, cpu = cpu_usage, ram = ram_usage )