#
#   Written by:  Mark W Kiehl
#   http://mechatronicsolutionsllc.com/
#   http://www.savvysolutions.info/savvycodesolutions/

# Copyright (C) Mechatroinc Solutions LLC
# License:  MIT


# Define the script version in terms of Semantic Versioning (SemVer)
# when Git or other versioning systems are not employed.
__version__ = "0.0.0"
from pathlib import Path
print("'" + Path(__file__).stem + ".py'  v" + __version__)


# Make sure Windows environment variable CLOUDSDK_PYTHON is set
#import os
#if not "CLOUDSDK_PYTHON" in os.environ: raise Exception("Windows environment variable CLOUDSDK_PYTHON not configured!")
#print("\nIMPORTANT: make sure to set Windows environment variable CLOUDSDK_PYTHON in gconsole")
#print("set CLOUDSDK_PYTHON=C:\\Users\\Mark Kiehl\\AppData\\Local\\Programs\\Python\\Python312\\python.exe\n")


"""

Make sure Windows environment variable CLOUDSDK_PYTHON is set
set CLOUDSDK_PYTHON=C:\\Users\\Mark Kiehl\\AppData\\Local\\Programs\\Python\\Python312\\python.exe

See template.py for how to configure Google Cloud Platform (GCP) with a project, a service account, and authentication

GCP Pub/Sub

https://cloud.google.com/pubsub/docs/pubsub-basics
https://cloud.google.com/pubsub/docs/publish-receive-messages-client-library#pubsub-client-libraries-python


Steps:
- Create a project
  See if a project already exists and Python is configured properly:
    $ gcloud info
    $ gcloud config list
- Enable the Pub/Sub API
  $ gcloud services enable pubsub.googleapis.com
- Install Python client library
  pip install --upgrade google-cloud-pubsub
- Enable permissions
  $ gcloud auth application-default login
- List any topics that exist 
  $ gcloud pubsub topics list
- Create a Pub/Sub topic and a subscription
  $ gcloud pubsub topics create my-topic
  $ gcloud pubsub topics create raw-streaming-topic
  output: Created topic [projects/data-platform-2024/topics/raw-streaming-topic].
- Use the gcloud pubsub subscriptions create command to create a subscription.
  $ gcloud pubsub subscriptions create my-sub --topic my-topic
  $ gcloud pubsub subscriptions create raw_streaming-subscription --topic raw-streaming-topic
  output: Created subscription [projects/data-platform-2024/subscriptions/raw_streaming-subscription].
- Use the gcloud CLI to test publishing a message to topic raw-streaming-topic
  $ gcloud pubsub topics publish my-topic --message="hello"
  $ gcloud pubsub topics publish raw-streaming-topic --message="message #1"
- Use gcloud CLI to test subscribing to topic raw-streaming-topic
  $ gcloud pubsub subscriptions pull my-sub --auto-ack
  $ gcloud pubsub subscriptions pull raw_streaming-subscription --auto-ack
- Run the Python scripts
- Use the gcloud CLI to clean up and avoid incurring charges to your Google Cloud account 
  $ gcloud pubsub subscriptions delete raw_streaming-subscription
  $ gcloud pubsub topics delete raw-streaming-topic

  

  roles: roles/pubsub.admin

"""


# IMPORTANT:
# Do not use library 'orjson'.  Alpine Linux cannot use wheels from PyPI.  



def gcp_json_credentials_exist(verbose=False):
    """

    https://cloud.google.com/docs/authentication/application-default-credentials#personal
    """

    from pathlib import Path
    from savvy_os import savvy_get_os
    import os 

    if savvy_get_os() == "Windows":
        # Windows: %APPDATA%\gcloud\application_default_credentials.json
        path_gcloud = Path(Path.home()).joinpath("AppData\\Roaming\\gcloud")
        if not path_gcloud.exists():
            print("WARNING:  Google CLI folder not found: " + str(path_gcloud))
            #raise Exception("Google CLI has not been installed!")
            return False

        path_file_json = path_gcloud.joinpath("application_default_credentials.json")
        if not path_file_json.exists() or not path_file_json.is_file():
            print("WARNING: Application Default Credential JSON file missing: "+ str(path_file_json))
            #raise Exception("File not found: " + str(path_file_json))
            return False
        
        if verbose: print(str(path_file_json))
        return True
    else:
        # Linux, macOS: 
        # $HOME/.config/gcloud/application_default_credentials.json
        # //root/.config/gcloud/application_default_credentials.json
        path_gcloud = Path(Path.home()).joinpath(".config/gcloud/")
        if not path_gcloud.exists():
            print("Path.home(): ", str(Path.home()))
            print("WARNING:  Google CLI folder not found: " + str(path_gcloud))
            # WARNING:  Google CLI folder not found: /.config/gcloud
            #raise Exception("Google CLI has not been installed!")
            return False
        path_file_json = path_gcloud.joinpath("application_default_credentials.json")
        if not path_file_json.exists() or not path_file_json.is_file():
            print("WARNING: Application Default Credential JSON file missing: "+ str(path_file_json))
            # /root/.config/gcloud/application_default_credentials.json
            #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] ='$HOME/.config/gcloud/application_default_credentials.json'
            #raise Exception("File not found: " + str(path_file_json))
            return False
        
        if verbose: print(str(path_file_json))
        # /root/.config/gcloud/application_default_credentials.json
        return True


def gcp_pub_sub_check_permissions(project_id=None, verbose=True):
    """
    Returns True if permissions are configured for GCP Pub/Sub

    """

    # pip install --upgrade google-cloud-pubsub
    #from google.cloud import pubsub_v1

    from google.cloud import resourcemanager_v3
    from google.iam.v1 import iam_policy_pb2

    #import os.path
    from pathlib import Path
    from savvy_os import savvy_get_os

    if savvy_get_os() == "Windows":
        path_gcloud = Path(Path.home()).joinpath("AppData\\Roaming\\gcloud")
        if not path_gcloud.exists():
            print("WARNING:  Google CLI folder not found: " + str(path_gcloud))
            #raise Exception("Google CLI has not been installed!")

        path_file_json = path_gcloud.joinpath("application_default_credentials.json")
        if not path_file_json.exists() or not path_file_json.is_file():
            print("WARNING: Application Default Credential JSON file missing: "+ str(path_file_json))
            #raise Exception("File not found: " + str(path_file_json))
    else:
        print("WARNING:  Existance of application_default_credentials.json not checked because OS is " + savvy_get_os())

    # below derived from get_project_policy in api_gcp_iam.py
    e = None
    try:
        client = resourcemanager_v3.ProjectsClient()
    except Exception as e:
        if verbose: print(e)
        return False, e
    
    request = iam_policy_pb2.GetIamPolicyRequest()
    request.resource = f"projects/{project_id}"

    try:
        policy = client.get_iam_policy(request)
    except Exception as e:
        if verbose: 
            print(request.resource)
            print(e)
        return False, e
        
    return True, None




def gcp_pubsub_get_topics(project_id=None, timeout_s=15, verbose=True):
    # pip install --upgrade google-cloud-pubsub
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()


    # Get a list of Pub/Sub topics for a project
    # permissions required: pubsub.topics.list  or roles/pubsub.editor
    # https://cloud.google.com/pubsub/docs/list-topics#expandable-1

    #  $ gcloud alpha pubsub topics add-iam-policy-binding my-topic --member='iam-account=data-platform-2024-svc-act@data-platform-2024.iam.gserviceaccount.com' --role='roles/editor'    
    #  $ gcloud pubsub topics add-iam-policy-binding my-topic --member='iam-account=data-platform-2024-svc-act@data-platform-2024.iam.gserviceaccount.com' --role='roles/pubsub.editor'    
    #  $ gcloud projects add-iam-policy-binding my-topic --member='iam-account=data-platform-2024-svc-act@data-platform-2024.iam.gserviceaccount.com' --role='roles/pubsub.editor'    


    #project_path = f"projects/{project_id}"
    project_path = "projects/" + project_id + ""
    #print(project_path)     # projects/data-platform-2024

    topics = []
    if verbose: print("Pub/Sub topics for " + project_path + ":")

    try:
        pub_sub_topics = publisher.list_topics(request={"project": project_path}, timeout=timeout_s)
    except Exception as e:
        print("ERROR: .list_topics() " + str(e))
        return topics

    for topic in pub_sub_topics:
        if verbose: print("\t",topic.name, topic.state, topic.message_retention_duration)
        topics.append(topic)

    return topics


def gcp_pubsub_create_topic(project_id=None, topic_id="", timeout_s=15, verbose=True):
    # Create Topic
    # https://cloud.google.com/pubsub/docs/create-topic#create_a_topic_2

    # pip install --upgrade google-cloud-pubsub
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(project_id, topic_id)
    #print(topic_path)   # projects/data-platform-2024/topics/raw-streaming-topic

    try:
        topic = publisher.create_topic(request={"name": topic_path}, timeout=timeout_s)
    except Exception as e:
        if verbose: print("ERROR: " + str(e))
        return False

    #print(type(topic))      # <class 'google.cloud.pubsub_v1.types.Topic'>
    if verbose: print("Created topic " + topic.name + " for project " + project_id)

    return True


def gcp_pubsub_delete_topic(topic_path="", timeout_s=15, verbose=True):
    # https://cloud.google.com/pubsub/docs/create-topic#create_a_topic_2

    # pip install --upgrade google-cloud-pubsub
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()

    # Pub/Sub resource name (topic_path):
    # https://cloud.google.com/pubsub/docs/pubsub-basics#resource_names
    # format:  projects/project-identifier/topic/ID
    # format:  projects/project-identifier/subscriptions/ID

    try:
        #publisher.delete_topic(request={"name": topic_path}, timeout=timeout_s)
        publisher.delete_topic(request={"topic": topic_path}, timeout=timeout_s)
    except Exception as e:
        if verbose: print("ERROR: " + str(e))
        return False

    #print(type(topic))      # <class 'google.cloud.pubsub_v1.types.Topic'>
    if verbose: print("Successfully deleted topic " + topic_path)

    return True



def gcp_pubsub_get_subscriptions(project_id=None, verbose=True):

    from google.cloud import pubsub_v1

    subscriber = pubsub_v1.SubscriberClient()
    project_path = f"projects/{project_id}"
    if verbose: print("project_path: " + str(project_path))

    subscriptions = []

    # Wrap the subscriber in a 'with' block to automatically call close() to
    # close the underlying gRPC channel when done.
    with subscriber:
        for subscription in subscriber.list_subscriptions(request={"project": project_path}):
            subscriptions.append(subscription.name)
            if verbose: print("\t" + subscription.name)

    return subscriptions


def gcp_pubsub_create_pull_subscription(project_id=None, topic_id=None, subscription_id=None, enable_exactly_once_delivery=True, verbose=True):

    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    if verbose: print("subscription_path: ", subscription_path)

    # Wrap the subscriber in a 'with' block to automatically call close() to
    # close the underlying gRPC channel when done.
    success = True
    with subscriber:
        try:
            # enable payload unwrapping push delivery for a subscription
            # https://cloud.google.com/pubsub/docs/payload-unwrapping#configure_payload_unwrapping
            subscription = subscriber.create_subscription(
                request={"name": subscription_path, 
                         "topic": topic_path, 
                         "enable_exactly_once_delivery": enable_exactly_once_delivery,
                        }
            )
        except Exception as e:
            if verbose: print("ERROR: " + str(e))
            success = False
        
    if success == True:
        if verbose: 
            if enable_exactly_once_delivery:
                print("Subscription created with exactly_once_delivery: ", subscription)
            else:
                print("Subscription created: ", subscription)
        return True
    else:
        return False



# ---------------------------------------------------------------------------

# pip install numpy


def create_data_packet(packet_type='JSON', channels=3, source=None, verbose=False):
    """
    Returns a JSON serialized data packet consisting of data and metadata.
    
    The data:
        datetime_created
        unix_ms
        payload

    The size of the payload (# of values) corresponds to the value for argument 'channels'. Random np.float32 values are returned in a numpy 1D array.
        
    b'{"datetime_created":"2024-08-23T16:08:57.604388+00:00","unix_ms":1724443737000.0,"payload":[8.598089e-39,-1.6940384e38,4.043461e-39,9.399784e37,-2.201807e-39]}'

    The metadata:
        'business': 'Mechatronic Solutions LLC',
        'latitude': 40.44127,
        'longitude': -76.12276,
        'unix_ms': 1679828219121,
        'time': '2023-03-26T10:58:59+0000',  # ISO-8601
        "source": [Fn argument "source"],

    """
    from pathlib import Path
    from datetime import datetime, timezone
    import time
    # pip install numpy
    import numpy as np

    import json
    from datetime import datetime, timezone
    from time import mktime
    from math import sin, exp

    if source is None: raise Exception("Argument 'source' was not passsed.")

    # Create and populate a data packet

    # Get the datetime now in UTC as an object and in Unix ms
    datetime_created = datetime.now(tz=timezone.utc)
    unix_ms = mktime(datetime_created.timetuple()) * 1000.0

    # Calculate x from unix_ms
    x = (unix_ms / 10**(len(str(int(unix_ms)))-0))

    # Remove integer part of x
    x = x - float(int(x))

    payload = []
    col_labels = []
    col_labels.append("unix_ms")
    for c in range(0, channels):
        if c == 0: 
            y = x
            col_labels.append("raw")
        elif c == 1: 
            if x < 1.0:
                y = sin(x)
            else:
                y = sin(1.0/x)
            col_labels.append("cyc1")
        elif c == 2:
            y = x**4 + x**3 + x**2 + x
            col_labels.append("poly")
        elif c == 3: 
            y = float(c) * x + float(1/c)
            col_labels.append("lin1")
        elif c == 4:
            if x < 1.0:
                y = sin(x)
            else:
                y = sin(1.0/x)
            y = 10.0*x + x*10.0
            col_labels.append("cyc2")
        elif c==5:
            y = x**2
            col_labels.append("square")
        elif c==6:
            y = x**3
            col_labels.append("cubic")
        elif c == 7: 
            y = float(-1/c)*x + float(1/c)
            col_labels.append("lin2")
        elif c==8:
            try:
                y = exp(x)
            except Exception as e:
                y = x**4 + x**3 + x**2 + x
            col_labels.append("exp")
        else:
            # c > 8
            try:
                y = x**4 + x**3 + x**2 + x
            except Exception as e:
                y = x
            col_labels.append("ch" + str(c))

        payload.append(y)


    """
    payload = []
    for i in range(0, channels):
        if i%2==0: 
            # Create a small +/- float
            payload.append(float(np.random.uniform(-1.18E-38, +1.18E-38)))
        else:
            # create a large +/- float
            payload.append(float(np.random.uniform(-3.4E+38, +3.4E+38)))

    """

    # datetime_created must be converted to a string for JSON serialization
    data = {
        "datetime_created": datetime_created.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
        "unix_ms": time.mktime(datetime_created.timetuple()) * 1000,        # DateTime to Unix timestamp milliseconds
        "pub_region": source,
        "payload": json.dumps(payload)
    }


    if packet_type == 'JSON':
        #JSON serialize data and encode it
        data = json.dumps(data).encode('utf-8')
        # Cannot use orjson with Linux, but below is how to do it
        #data = orjson.dumps(data, option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY)
        #print(data) 
        # b'{"datetime_created":"2024-08-23T16:08:57.604388+00:00","unix_ms":1724443737000.0,"payload":[8.598089e-39,-1.6940384e38,4.043461e-39,9.399784e37,-2.201807e-39]}'
    else:
        raise Exception("packet_type of '" + str(packet_type) + "' not currently supported")
    
    return data



if __name__ == '__main__':
    pass

    # General documentation for Python pub/sub: https://cloud.google.com/python/docs/reference/pubsub/latest

    # project id: data-platform-2024
    # service account: data-platform-2024-svc-act@data-platform-2024.iam.gserviceaccount.com
    # service-208633038463@gcp-sa-pubsub.iam.gserviceaccount.com

    PROJECT_ID = "data-platform-v1-2"
    TIMEOUT_S = 15.0  

    # ---------------------------------------------------------------------------
    # Check that credentials exist for a project

    """
    #project_id = "data-platform-v1-2"
    result, e = gcp_pub_sub_check_permissions(project_id=PROJECT_ID, verbose=False)
    if not result:
        #print(e)
        raise Exception(e)
    else:
        print("gcp_pub_sub_check_permissions()=True for project " + PROJECT_ID + "\n")
    """

    # ---------------------------------------------------------------------------
    # Send data packet to to GCP pub/sub

    """
    import time
    import random

    def send_data_packet_to_gcp_pub(project_id=None, topic_id=None, verbose=True):

        # pip install --upgrade google-cloud-pubsub
        from concurrent.futures import TimeoutError
        from google.cloud import pubsub_v1

        topics = gcp_pubsub_get_topics(project_id=PROJECT_ID, verbose=False)
        if verbose: print(str(len(topics)) + " topics found for project " + PROJECT_ID)
        exists = False
        for topic in topics:
            if verbose: print("\t", topic.name)
            topic_name = str(topic.name).split("/")
            topic_name = topic_name[len(topic_name)-1]
            #print("\ttopic_name:'" + topic_name + "'")
            if topic_name == topic_id: exists = True
        
        if not exists:
            # Create topic topic_id
            if not gcp_pubsub_create_topic(project_id=project_id, topic_id=topic_id, verbose=False): 
                raise Exception("Unable to create topic '" + topic_id + "' for project '" + project_id + "'")
            else:
                if verbose: print("Successfully created topic '" + topic_id + "' for project '" + project_id + "'\n")
        
        publisher = pubsub_v1.PublisherClient()
        # The `topic_path` method creates a fully qualified identifier
        # in the form `projects/{project_id}/topics/{topic_id}`
        topic_path = publisher.topic_path(project_id, topic_id)
        if verbose: print("topic_path: ", topic_path)
        # topic_path:  projects/data-platform-2024/topics/raw_streaming

        data_packet = create_data_packet(channels=5)
        print(data_packet)
        # {"datetime_created":"2024-09-01T15:37:50.639435+00:00","unix_ms":1725219470000.0,"source":"api_gcp_pub-sub.py","payload":[-8.334515e-39,-3.249203e38,1.0373193e-38,1.98253e38,7.008128e-39]}

        # Create custom metadata as a dictionary
        custom_meta_content = {
            'business': 'Mechatronic Solutions LLC',
            'latitude': 40.44127,
            'longitude': -76.12276,
            'unix_ms': 1679828219121,
            'time': '2023-03-26T10:58:59+0000'  # ISO-8601
        }

        # When you publish a message, the client returns a future.  timeout=600 s is default
        # This method may block if LimitExceededBehavior.BLOCK is used in the flow control settings.
        # pubsub_v1.publisher.exceptions.MessageTooLargeError: If publishing the message would exceed the max size limit on the backend.
        try: 
            future = publisher.publish(topic_path, data_packet, timeout=timeout_s)
        except Exception as e:
            print("ERROR: " + str(e))
            print(future.result())
            return False
        
        if verbose: print(future.result())
        return True
        

    topic_id = "streaming_data_packet_v1-0-0"
    # gcloud pubsub topics publish streaming_data_packet_v1-0-0 --message="message #1"

    while True:
        if not send_data_packet_to_gcp_pub(project_id=project_id, topic_id=topic_id, verbose=False): 
            raise Exception("Error sending data packet to " + project_id + " | " + topic_id)
        else:
            print("Successfully sent the data packet to project_id " + project_id + ", topic_id " + topic_id)
        t = random.randint(30,90)
        print("Next send in " + str(t) + " sec..")
        time.sleep(t)     # random pause of 30 to 90 seconds
    
    """


    # ---------------------------------------------------------------------------
    # create_data_packet()

    """
    #data_packet = create_data_packet(channels=5)
    #print(data_packet)
    # b'{"datetime_created": "2024-09-17T11:27:36.118994+0000", "unix_ms": 1726586856000.0, "source": "api_gcp_pub_sub.py", "payload": "[0.1726586856, 0.17180210806571325, 0.20850553615408005, 0.8513093901333333, 3.453173712]"}'
    """

    # Development of create_data_packet()
    # Requires Pandas v2
    # Create time series data from unix_ms
    """
    # pip install pandas
    import pandas as pd
    import matplotlib.pyplot as plt

    from datetime import datetime, timezone
    from time import mktime
    from math import sin, exp

    scale_y = False
    channels = 3
    ts = []
    
    rows = 1000       

    # Define below the increment in ms between each sample.  
    # 60000 ms = 1 min      works well with rows=1440
    # 3.6e+6 ms = 1 hr
    # 8.64e+7 ms = 1 day
    # 3.154e+10 ms = 1 yr
    unix_ms_inc = 60000*2
    print("Total time span of the data for " + str(rows) + " rows will be ", round((unix_ms_inc*rows)/3.6e+6,1), "h or ", round(unix_ms_inc*rows/8.64e+7,1), "d or ", round(unix_ms_inc*rows,0), "ms")
    
    unix_ms = mktime(datetime.now(tz=timezone.utc).timetuple()) * 1000.0
    

    for i in range(0,rows):
        row = []

        # increment unix_ms to simulate executions in the future
        unix_ms += unix_ms_inc

        # Calculate x from unix_ms
        x = (unix_ms / 10**(len(str(int(unix_ms)))-0))
        
        # Scale x based on unix_ms_inc*rows
        if scale_y: 
            if unix_ms_inc*rows <= 6.0e6: x = x*1e6   # < 1.7 h
            elif unix_ms_inc*rows <= 8.64e7: x = x*1e5   # < 24 h
            #elif unix_ms_inc*rows <= 8.64e+8: x = x*1e3   # < 240 h or 10 d
            elif unix_ms_inc*rows <= 8.64e+7: x = x*1e0    # 1 day
            else: 
                #1 yr = 3.154e+10
                x = x
        
        # Remove integer part of x
        x = x - float(int(x))

        row.append(unix_ms)
        payload = []
        col_labels = []
        col_labels.append("unix_ms")
        for c in range(0, channels):
            if c == 0: 
                y = x
                col_labels.append("raw")
            elif c == 1: 
                if x < 1.0:
                    y = sin(x)
                else:
                    y = sin(1.0/x)
                col_labels.append("cyc1")
            elif c == 2:
                y = x**4 + x**3 + x**2 + x
                col_labels.append("poly")
            elif c == 3: 
                y = float(c) * x + float(1/c)
                col_labels.append("lin1")
            elif c == 4:
                if x < 1.0:
                    y = sin(x)
                else:
                    y = sin(1.0/x)
                y = 10.0*x + x*10.0
                col_labels.append("cyc2")
            elif c==5:
                y = x**2
                col_labels.append("square")
            elif c==6:
                y = x**3
                col_labels.append("cubic")
            elif c == 7: 
                y = float(-1/c)*x + float(1/c)
                col_labels.append("lin2")
            elif c==8:
                try:
                    y = exp(x)
                except Exception as e:
                    y = x**4 + x**3 + x**2 + x
                col_labels.append("exp")
            else:
                # c > 8
                try:
                    y = x**4 + x**3 + x**2 + x
                except Exception as e:
                    y = x
                col_labels.append("ch" + str(c))

            payload.append(y)
            row.append(y)
        ts.append(row)

        #print(row)  # [1726431620000.0, 0.8660254037844386, 0.8660254037844386, 0.8660254037844386]
    #print(col_labels)

    # "payload":[8.598089e-39,-1.6940384e38,4.043461e-39,9.399784e37,-2.201807e-39]
    #print(ts)   # [[1726431616000.0, 0.0, 0.0, 0.0], [1726431617000.0, 0.25881904510252074, 0.25881904510252074, 0.25881904510252074], [1726431618000.0, 0.49999999999999994, 0.49999999999999994, 0.49999999999999994], [1726431619000.0, 0.7071067811865476, 0.7071067811865476, 0.7071067811865476], [1726431620000.0, 0.8660254037844386, 0.8660254037844386, 0.8660254037844386]]
    
    # Generate a dataframe
    df = pd.DataFrame(ts, columns=col_labels)
    df.set_index('unix_ms', inplace=True)
    print(df)
    #                   raw      cyc1      lin1      poly
    #unix_ms
    #1.726508e+12  0.507998  0.486429  1.515996  0.963751
    #1.726508e+12  0.508058  0.486481  1.516116  0.963950
    #...                ...       ...       ...       ...
    #1.726594e+12  0.594338  0.559960  1.688676  1.282295
    
    # matplotlib subplots stacked in vertical directionplt.legend
    fig, ax = plt.subplots(df.shape[1], figsize=(10,6), sharex=True)     #sharex synchronizes the x-axis across all plots
    fig.suptitle("payload")
    i = 0
    for c in df.columns:
        ax[i].plot(df.index, df[c])       # ax[0] is the top plot
        ax[i].title.set_text(c)
        ax[i].tick_params(axis="x", rotation=25, labelsize=6) 
        i += 1
    plt.tight_layout()  # makes the dialog fit the content
    plt.show()
    """


    # ---------------------------------------------------------------------------
    # Get topics by project
 
    """
    project_id = "data-platform-v1-2"
    timeout_s = 15.0  

    topics = gcp_pubsub_get_topics(project_id=project_id, verbose=False)
    print(str(len(topics)) + " topics found for project " + project_id)
    for topic in topics:
        print("\t", topic.name)
    """

    # ---------------------------------------------------------------------------
    # Create topic for a project

    """
    project_id = "data-platform-v1-2"
    timeout_s = 15.0  
    topic_id = "topic_1"


    
    if not gcp_pubsub_create_topic(project_id=project_id, topic_id=topic_id, verbose=False): 
        raise Exception("Unable to create topic '" + topic_id + "' for project '" + project_id + "'")
    else:
        print("Successfully created topic '" + topic_id + "' for project '" + project_id + "'\n")
    """

    # ---------------------------------------------------------------------------
    # Delete all topics for a project
 
    """
    project_id = "data-platform-v1-2"
    timeout_s = 15.0  

    topics = gcp_pubsub_get_topics(project_id=project_id, verbose=False)
    print("Deleting " + str(len(topics)) + " topics found for project " + project_id)
    for topic in topics:
        #print("\t", topic.name)
        topic_id = topic.name
        if not gcp_pubsub_delete_topic(topic_path=topic.name, verbose=False): 
            raise Exception("Failed to delete topic '" + topic_id + "' for project " + project_id + "\n")
        else:
            print("\tSuccessfully deleted topic: " + topic_id + "\n")
    """

    # ---------------------------------------------------------------------------
    # Pull subscribe with exactly-once message delivery  (read messages for a subscription)
    # https://cloud.google.com/pubsub/docs/exactly-once-delivery#subscribe_with_exactly-once_message_delivery

    """
    # Get the exactly-once message for a subscription
    project_id = "data-platform-v1-2"
    timeout_s = 600.0  
    subscriptions = gcp_pubsub_get_subscriptions(project_id=project_id, verbose=False)
    print(str(len(subscriptions)) + " subscriptions:")
    for subscription in subscriptions:
        print("\t" + subscription)
        subscription_path = subscription
        subscription_id = str(subscription_path).split("/")
        subscription_id = subscription_id[len(subscription_id)-1]
        gcp_pubsub_get_pull_subscription_message(project_id=project_id, subscription_id=subscription_id, timeout_s=timeout_s, verbose=True)
    """


    # ---------------------------------------------------------------------------
    # Delete all subscriptions by project_id


    """
    from google.cloud import pubsub_v1

    subscriber = pubsub_v1.SubscriberClient()

    project_id = "data-platform-v1-2"
    subscriptions = gcp_pubsub_get_subscriptions(project_id=project_id, verbose=False)
    print(str(len(subscriptions)) + " subscriptions:")
    for subscription in subscriptions:
        print("\t" + subscription)
        subscription_path = subscription
    
        #subscription_path = subscriber.subscription_path(project_id, subscription_id)

        # Wrap the subscriber in a 'with' block to automatically call close() to
        # close the underlying gRPC channel when done.
        deleted = True
        with subscriber:
            try:
                subscriber.delete_subscription(request={"subscription": subscription_path})
            except Exception as e:
                print("ERROR: " + str(e))
                deleted = False

        if deleted: print("\tSubscription deleted: " + str(subscription_path))
    """

    # ---------------------------------------------------------------------------
    # List subscriptions
    # https://cloud.google.com/pubsub/docs/create-subscription#pubsub_create_pull_subscription-python

    """
    project_id = "data-platform-v1-2"
    subscriptions = gcp_pubsub_get_subscriptions(project_id=project_id, verbose=False)
    print(str(len(subscriptions)) + " subscriptions:")
    for subscription in subscriptions:
        print("\t" + subscription)
    """

    # $ gcloud pubsub subscriptions pull streaming_data_packet_sub_v1-0-0 --auto-ack

    # ---------------------------------------------------------------------------
    # Create a pull subscription
    # https://cloud.google.com/pubsub/docs/create-subscription#pubsub_create_pull_subscription-python


    """
    project_id = "data-platform-v1-2"
    topic_id = "streaming_data_packet_v1-0-0"
    subscription_id = "streaming_data_packet_sub_v1-0-0"

    if not gcp_pubsub_create_pull_subscription(project_id=project_id, topic_id=topic_id, subscription_id=subscription_id): raise Exception("Subscription pull failed!")
    """

    # ---------------------------------------------------------------------------
    # Receive messages (pull) 
    # https://cloud.google.com/pubsub/docs/publish-receive-messages-client-library#pubsub-client-libraries-python

    # *** SEE gcp_pubsub_get_pull_subscription_message() ***
    # gcp_pubsub_get_pull_subscription_message() uses pull with enable_exactly_once_delivery

    """
    # pip install --upgrade google-cloud-pubsub
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1

    project_id = "data-platform-v1-2"
    subscription_id = "streaming_data_packet_sub_v1-0-0"
    timeout_s = 60.0

    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.")
        # message.attributes:
        #    print("Attributes:")
        #    for key in message.attributes:
        #        value = message.attributes.get(key)
        #        print(f"{key}: {value}")
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely, unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout_s)
        except TimeoutError:
            print("The listening timeout of " + str(timeout_s) + "s was reached.")
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.
        except Exception as e:
            print("ERROR: " + str(e))

    #Listening for messages on projects/data-platform-2024/subscriptions/raw_streaming-subscription..
    #
    #Received Message {
    #  data: b'Message number 5'
    #  ordering_key: ''
    #  attributes: {}
    #}.
    # ...
   """


    # ---------------------------------------------------------------------------
    # Publish messages to topic 'raw_streaming' 
    # https://cloud.google.com/pubsub/docs/publish-receive-messages-client-library#pubsub-client-libraries-python

    """
    from google.cloud import pubsub_v1

    project_id = "data-platform-2024"
    topic_id = "raw-streaming-topic"
    # Number of seconds the publisher should try to send a message
    timeout = 15.0

    publisher = pubsub_v1.PublisherClient()
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    topic_path = publisher.topic_path(project_id, topic_id)
    print("topic_path: ", topic_path)
    # topic_path:  projects/data-platform-2024/topics/raw_streaming

    for n in range(1, 10):
        data_str = f"Message number {n}"
        # Data must be a bytestring
        data = data_str.encode("utf-8")
        print("Ready to publish msg " + str(n) + ": " + str(data) + "..")
        # When you publish a message, the client returns a future.  timeout=600 s is default
        # This method may block if LimitExceededBehavior.BLOCK is used in the flow control settings.
        future = publisher.publish(topic_path, data, timeout=timeout)
        print(future.result())
    
    print(f"Published messages to {topic_path}.")
    # exception: 503 failed to connect to all addresses; last error: UNKNOWN: ipv4:172.217.12.138:443: tcp handshaker shutdown
    # If the above happens, must reconfigure IAM
    """

    # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------
    # Create pull subscriptions
    # https://cloud.google.com/pubsub/docs/create-subscription
