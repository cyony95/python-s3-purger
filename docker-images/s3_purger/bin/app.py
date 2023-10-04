import boto3
import time
import os
from botocore.exceptions import ClientError
from prometheus_api_client import PrometheusConnect
import gc
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#s3 config
access_key = os.getenv('ACCESS_KEY')
secret_key = os.getenv('SECRET_KEY')
endpoint_url = os.getenv('S3_ENDPOINT_URL')
bucket_name = os.getenv('BUCKET_NAME')
prometheus_url = 'http://kube-prometheus-stack-prometheus.monitoring:9090'
metric = 'ontaps3_size'

s3_target = boto3.resource('s3', 
    endpoint_url = endpoint_url,
    aws_access_key_id = access_key,
    aws_secret_access_key = secret_key,
    aws_session_token = None,
    config = boto3.session.Config(signature_version = 's3v4'),
    verify = False
)


def calculate_total_bucket_size(bucket_name, prometheus_url, metric):
    try:
        label = {'bucket': bucket_name}
        prom = PrometheusConnect(url = prometheus_url, disable_ssl = True)
        metric_data = prom.get_current_metric_value(metric_name = metric, label_config = label)
        bucket_size = int(metric_data[0]['value'][1])
        if bucket_size:
            return bucket_size
        else:
            print(f'Prometheus returns no values for the metric {metric}. Please check Prometheus and Harvest.')
    except Exception as e:
        print (e)
        print (f"Could not retrieve allocated bucket size from Prometheus, please check that the {metric} is available in Prometheus,\nharvest is installed and running and Netapp management IP is present in the inventory")


# Calculates the occupied size and adds all filenames and their dates to a dictionary
def bucket_size_and_items(s3):
    print("Calculating occupied size and constructing file list dictionary...")
    size_byte = 0
    items = {}
    try:
        for obj in s3.Bucket(bucket_name).objects.all():
            size_byte = size_byte+obj.size
            items[obj.key] = obj.last_modified
        return size_byte, items
    except Exception as e:
        print (e)

gc.collect()
file_list = {}


while(1):
    total_bucket_size_byte = os.getenv('BUCKET_SIZE')
    size, file_list = bucket_size_and_items(s3_target)
    print(f'Total bucket size is {total_bucket_size_byte/1024/1024/1024} GB.')
    print(f'Occupied bucket size is {size/1024/1024/1024} GB.')
    print(f'Bucket is {100*(size/total_bucket_size_byte)}% full.')
    # Sorting the files from oldest to newest
    file_list_sorted = dict(sorted(file_list.items(), key=lambda x: x[1]))
    # Checking for high watermark
    if (size >= 0.95 * total_bucket_size_byte):
        print ("Free space is less than 5%. Starting emergency deletion...")
        new_size_byte = size
        for filename in file_list_sorted.copy().keys():
            try:
                # Checking for low watermark
                if new_size_byte <= 0.90 * total_bucket_size_byte:
                    print("Free space is greater than 10%. Going back to sleep...")
                    break   
                if "index" not in filename:
                    file_size = s3_target.Object(bucket_name, filename).content_length
                    new_size_byte = new_size_byte - file_size
                    print(f"File {filename} deleted.")
                    s3_target.Object(bucket_name,filename).delete()
            except ClientError as e:
                if e.response['Error']['Code'] == "404":
                    # Object not found
                    print("The object does not exist. Continuing emergency deletion...")
                    continue
            except Exception as e:
                print(e)
    else:
        print("Free space is greater than 10%. Going back to sleep...")
    time.sleep(900)
