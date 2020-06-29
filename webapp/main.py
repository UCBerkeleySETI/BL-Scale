import os
import base64
import io
import re

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import zmq

import logging
from google.cloud import storage

from flask import Flask, render_template

global counter
counter = 0

# create and configure the app
test_config=None
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'bl.sqlite'),
)

if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
else:
    # load the test config if passed in
    app.config.from_mapping(test_config)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# a simple page that says hello
@app.route('/index')
@app.route('/')
def index():
    #NOT SURE IF WE NEED THIS YET
    def get_uri(bucket_name):
        #bucket_name = 'bl-scale'

        storage_client = storage.Client("BL-Scale")
        # Retrieve all blobs with a prefix matching the file.
        bucket=storage_client.get_bucket(bucket_name)
        print(bucket)
        # List blobs iterate in folder
        blobs=bucket.list_blobs()

        uris = []
        for blob in blobs:
            if "info_df.pkl" in blob.name:
                uris += ["gs://"+bucket_name+"/"+blob.name]
        return uris

    #string list of pickles
    uris = ['gs://bl-scale/GBT_58010_50176_HIP61317_fine/info_df.pkl', 'gs://bl-scale/GBT_58014_69579_HIP77629_fine/info_df.pkl', 'gs://bl-scale/GBT_58110_60123_HIP91926_fine/info_df.pkl', 'gs://bl-scale/GBT_58202_60970_B0329+54_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_37805_HIP103730_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_39862_HIP105504_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_40853_HIP106147_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_41185_HIP105761_fine/info_df.pkl', 'gs://bl-scale/GBT_58307_26947_J1935+1616_fine/info_df.pkl', 'gs://bl-scale/GBT_58452_79191_HIP115687_fine/info_df.pkl']

    #returns string observation
    def get_observation(uri_str):
        obs = re.search(r"([A-Z])\w+(\+\w+)*", uri_str)
        return obs.group(0)

    #returns string list of urls
    def get_img_url(df, observation):
        indexes = []
        samples_url = []
        blockn = []
        for row in df.itertuples():
            indexes += [row[1]]
            blockn += [row[4]]
        for i in range(0, len(indexes)):
                samples_url += ["https://storage.cloud.google.com/bl-scale/"+observation+"/filtered/"+str(blockn[i])+"/"+str(indexes[i])+".png"]
        return samples_url

    #return base64 string of histogram
    def get_base64_hist(df):
        plt.figure(figsize=(8,6))
        plt.hist(df["freqs"], bins = np.arange(min(df["freqs"]),max(df["freqs"]), 0.8116025973))
        plt.title("Histogram of Hits")
        plt.xlabel("Frequency [MHz]")
        plt.ylabel("Count")
        pic_IObytes = io.BytesIO()
        plt.savefig(pic_IObytes,  format='png')
        pic_IObytes.seek(0)
        pic_hash = base64.b64encode(pic_IObytes.read())
        base64_img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
        return base64_img

    #returns dataframe of 3*n filtered images
    def filter_images(df, n):
        #filter 1000 to 1400 freqs
        freq_1000_1400 = df[(df["freqs"] >= 1000) & (df["freqs"] <= 1400)]
        freq_1000_1400 = freq_1000_1400.sort_values("statistic", ascending=False).head(n)
        # std_stat_1000_1400 = np.std(freq_1000_1400["statistic"])
        # extr_1000_1400 = freq_1000_1400[freq_1000_1400["statistic"] >= 8*std_stat_1000_1400]

        #filter 1400 to 1700 freqs
        freq_1400_1700 = df[(df["freqs"] > 1400) & (df["freqs"] <= 1700)]
        freq_1400_1700 = freq_1400_1700.sort_values("statistic", ascending=False).head(n)
        # std_stat_1400_1700 = np.std(freq_1400_1700["statistic"])
        # extr_1400_1700 = freq_1400_1700[freq_1400_1700["statistic"] >= 7*std_stat_1400_1700]

        #filter 1700 plus freqs
        freq_1700 = df[df["freqs"] > 1700]
        freq_1700 = freq_1700.sort_values("statistic", ascending=False).head(n)
        # std_stat_1700 = np.std(freq_1700["statistic"])
        # extr_1700 = freq_1700[freq_1700["statistic"] >= 8*std_stat_1700]

        extr_all = pd.concat([freq_1000_1400, freq_1400_1700, freq_1700])
        return extr_all

    #Dictionary, observation name for key, string list of urls for value
    obs_filtered_url = {}
    #Dictionary, observation name for key, string base64 of histogram for value
    base64_obs = {}
    #iterate through every observation dataframe in uri list
    #fills in the obs_filtered_url and base64_obs dictionary to be passed into render_template

    for uri in uris:
        data = pd.read_pickle(uri)
        observ = get_observation(uri)
        base64_obs[observ] = get_base64_hist(data)
        processed_data = filter_images(data, 4)
        obs_filtered_url[observ] = get_img_url(processed_data, observ)

    global counter
    counter = counter + 1

    return render_template("index.html", title="Main Page", sample_urls=obs_filtered_url, plot_bytes=base64_obs, count=counter)

# @app.route('/count')
# def increment_counter():
#     counter+=1

import db
db.init_app(app)

import auth
app.register_blueprint(auth.bp)

import monitor
app.register_blueprint(monitor.bp)

if __name__ == '__main__':
    app.run()
