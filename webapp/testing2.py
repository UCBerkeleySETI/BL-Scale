import pandas as pd
import numpy as np
import re
import os
import base64
import io
import matplotlib.pyplot as plt


uris = ['gs://bl-scale/GBT_58010_50176_HIP61317_fine/info_df.pkl', 'gs://bl-scale/GBT_58014_69579_HIP77629_fine/info_df.pkl', 'gs://bl-scale/GBT_58110_60123_HIP91926_fine/info_df.pkl', 'gs://bl-scale/GBT_58202_60970_B0329+54_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_37805_HIP103730_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_39862_HIP105504_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_40853_HIP106147_fine/info_df.pkl', 'gs://bl-scale/GBT_58210_41185_HIP105761_fine/info_df.pkl', 'gs://bl-scale/GBT_58307_26947_J1935+1616_fine/info_df.pkl', 'gs://bl-scale/GBT_58452_79191_HIP115687_fine/info_df.pkl']

def get_observation(uri_str):
    obs = re.search(r"([A-Z])\w+", uri_str)
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

#returns dataframe of filtered images
def filter_images(df):
    #filter 1000 to 1400 freqs
    freq_1000_1400 = df[(df["freqs"] >= 1000) & (df["freqs"] <= 1400)]
    std_stat_1000_1400 = np.std(freq_1000_1400["statistic"])
    extr_1000_1400 = freq_1000_1400[freq_1000_1400["statistic"] >= 8*std_stat_1000_1400]

    #filter 1400 to 1700 freqs
    freq_1400_1700 = df[(df["freqs"] > 1400) & (df["freqs"] <= 1700)]
    std_stat_1400_1700 = np.std(freq_1400_1700["statistic"])
    extr_1400_1700 = freq_1400_1700[freq_1400_1700["statistic"] >= 7*std_stat_1400_1700]

    #filter 1700 plus freqs
    freq_1700 = df[df["freqs"] > 1700]
    std_stat_1700 = np.std(freq_1700["statistic"])
    extr_1700 = freq_1700[freq_1700["statistic"] >= 8*std_stat_1700]
    extr_all = pd.concat([extr_1000_1400, extr_1400_1700, extr_1700])
    return extr_all

obs_filtered_url = {}
base64_obs = {}
for uri in uris[:2]:
    data = pd.read_pickle(uri)
    observ = get_observation(uri)
    base64_obs[observ] = get_base64_hist(data)
    processed_data = filter_images(data)
    obs_filtered_url[observ] = get_img_url(processed_data, observ)
