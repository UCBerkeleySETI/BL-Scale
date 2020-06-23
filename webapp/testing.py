import logging
from google.cloud import storage

bucket_name = 'bl-scale'
#folder='/GBT_58010_50176_HIP61317_fine/info_df.pkl'
delimiter='/'
#file = 'bl-scale'

storage_client = storage.Client("BL-Scale")
# Retrieve all blobs with a prefix matching the file.
bucket=storage_client.get_bucket(bucket_name)
print(bucket)
# List blobs iterate in folder
blobs=bucket.list_blobs() # Excluding folder inside bucket

uri = []
for blob in blobs:
   if "info_df.pkl" in blob.name:
       uri += ["gs://"+bucket_name+"/"+blob.name]
       print(uri)
  # destination_uri = '{}/{}'.format(folder, blob.name)
   #blob.download_to_filename(destination_uri)
