import base64
import datetime
import io
import random
import re
import string
from os import path

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


from google.cloud import storage


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )

# Creates base64 encoding of the health of CPU and Ram
def get_base64_hist_monitor(list_cpu, list_ram, threshold):
    # Create the x axis for plot
    x = np.arange(len(list_cpu))
    # Use the dark theme plots
    plt.style.use("dark_background")
    plt.figure(figsize=(8, 6))
    # Plot the ram and the cpu list
    plt.plot(x, list_cpu)
    plt.plot(x, list_ram)
    # Labels
    plt.title("Health")
    plt.xlabel("Time")
    plt.ylabel("Percent Usage % ")
    plt.legend(['CPU', 'MEMORY'], loc='upper left')
    # Convert image into bytes
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes,  format='png')
    # Close plots to save memory
    plt.close("all")
    pic_IObytes.seek(0)
    # Convert to base 64
    pic_hash = base64.b64encode(pic_IObytes.read())
    base64_img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
    return base64_img

#  Function to fill list with zeros to initialize a pod's health
def fill_zeros(array, length):
    array = ([0] * (length - len(array))) + array
    return array

# Helps convert the timestamp values in Milliseconds since Epoch to readable date time string.
def convert_time_to_datetime(dict, time_stamp_key="start_timestamp"):
    for k in dict:
        if time_stamp_key in dict[k]:
            temp = dict[k][time_stamp_key]
            temp = temp/1000
            date_time = datetime.datetime.fromtimestamp(temp).strftime('%c')
            dict[k][time_stamp_key] = date_time
    return dict

# Rounding values from the dictionary


def round_processing_time(dict):
    for obs in dict:
        if "processing_time" in dict[obs]:
            dict[obs]["processing_time"] = np.round(dict[obs]["processing_time"] / 60, decimals=2)
    return dict

# Includes rounding of time and converting timestamp to a date.


def process_message_dict(message_dict, time_stamp_key="start_timestamp"):
    message_dict = convert_time_to_datetime(message_dict, time_stamp_key=time_stamp_key)
    message_dict = round_processing_time(message_dict)
    for obs in message_dict:
        if "filename" not in message_dict[obs]:
            message_dict[obs]["filename"] = message_dict[obs]["url"]
    return message_dict

# # Intakes a string uri taken from the file on GCP
# # Returns the string observation name
#
#
# def get_observation(uri_str):
#     obs = re.search(r"([A-Z])\w+(\+\w+)*", uri_str)
#     return obs.group(0)
#
# # Intakes a pandas dataframe and string observation name
# # Returns a list of image urls
# # Use get_base64_images(observation_name) function instead of this
#
#
# def get_img_url(df, observation):
#     indexes = []
#     samples_url = []
#     blockn = []
#     for row in df.itertuples():
#         indexes += [row[1]]
#         blockn += [row[4]]
#     for i in range(0, len(indexes)):
#         samples_url += ["https://storage.cloud.google.com/bl-scale/" +
#                         observation+"/filtered/"+str(blockn[i])+"/"+str(indexes[i])+".png"]
#     return samples_url
#
#
# def get_random_string(length):
#     letters = string.ascii_lowercase
#     result_str = ''.join(random.choice(letters) for i in range(length))
#     return result_str
#
# # Intakes a string observation name
# # Returns the base64 string of the images (use this for the images on the results page)
#
#
# def get_base64_images(observation_name):
#     # checks to see if you already have the file, else
#     # downloads the best_hits.npy file from the observation bucket
#     if path.exists(observation_name + "_best_hits.npy"):
#         print("Files already downloaded")
#     else:
#         download_blob("bl-scale", observation_name + "/best_hits.npy",
#                             observation_name + "_best_hits.npy")
#     img_array = np.load(observation_name + "_best_hits.npy")
#     base64_images = {}
#     for i in np.arange(0, img_array.shape[0]):
#         key = get_random_string(6)
#         rawBytes = io.BytesIO()
#         plt.imsave(rawBytes, arr=img_array[i], cmap="viridis")
#         rawBytes.seek(0)  # return to the start of the file
#         pic_hash = base64.b64encode(rawBytes.read())
#         img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
#         base64_images[key] = img
#     return base64_images
#
# # Intakes a pandas dataframe
# # Returns a base64 image of the generated histogram of frequence distribution
#
#
# def get_base64_hist(df):
#     plt.style.use("dark_background")
#     plt.figure(figsize=(8, 6))
#     plt.hist(df["freqs"], bins=np.arange(min(df["freqs"]), max(df["freqs"]), 0.8116025973))
#     plt.title("Histogram of Hits")
#     plt.xlabel("Frequency [MHz]")
#     plt.ylabel("Count")
#     pic_IObytes = io.BytesIO()
#     plt.savefig(pic_IObytes,  format='png')
#     pic_IObytes.seek(0)
#     pic_hash = base64.b64encode(pic_IObytes.read())
#     base64_img = "data:image/jpeg;base64, " + str(pic_hash.decode("utf8"))
#     return base64_img
#
# # Returns dataframe of 3*n filtered images with the most extreme s-values
#
#
# def filter_images(df, n):
#     # filter 1000 to 1400 freqs
#     freq_1000_1400 = df[(df["freqs"] >= 1000) & (df["freqs"] <= 1400)]
#     freq_1000_1400 = freq_1000_1400.sort_values("statistic", ascending=False).head(n)
#
#     # filter 1400 to 1700 freqs
#     freq_1400_1700 = df[(df["freqs"] > 1400) & (df["freqs"] <= 1700)]
#     freq_1400_1700 = freq_1400_1700.sort_values("statistic", ascending=False).head(n)
#
#     # filter 1700 plus freqs
#     freq_1700 = df[df["freqs"] > 1700]
#     freq_1700 = freq_1700.sort_values("statistic", ascending=False).head(n)
#
#     extr_all = pd.concat([freq_1000_1400, freq_1400_1700, freq_1700])
#     return extr_all
#
# # returns list of base64 string hist for first element, list of string image
# # urls for the second element. Intakes a string uri
#
#
# def get_processed_hist_and_img(single_uri):
#     try:
#         data = pd.read_pickle(single_uri)
#         observ = get_observation(single_uri)
#         return [get_base64_hist(data), get_base64_images(observ)]
#     except:
#         print("could not find file "+ single_uri)
