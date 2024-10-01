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


"""

Message publisher to Google Pub/Sub Service

"""

# pip install numpy
# pip install --upgrade google-cloud-pubsub

from api_gcp_pub_sub import gcp_json_credentials_exist, gcp_pubsub_get_topics, gcp_pubsub_create_topic, create_data_packet
from time import sleep, perf_counter
from savvy_os import savvy_get_os
from random import randint
import os


# ---------------------------------------------------------------------------
# CONGIGURE THE FOLLOWING PROJECT CONSTANTS: 

PROJECT_ID = "data-platform-v1-6"
TOPIC_ID = "streaming_data_packet_topic"

# ---------------------------------------------------------------------------


def send_data_packet_to_gcp_pub(project_id=None, topic_id=None, region=None, verbose=True):

    # pip install --upgrade google-cloud-pubsub
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1
    import json

    if region is None: raise Exception("The argument 'region' was not passed to the function.")

    # Get a list of topics for the project
    topics = gcp_pubsub_get_topics(project_id=project_id, verbose=False)
    #if verbose: print(str(len(topics)) + " topics found for project " + project_id)
    
    # Make sure a topic matching topic_id exists
    exists = False
    for topic in topics:
        #if verbose: print("\t", topic.name)
        topic_name = str(topic.name).split("/")
        topic_name = topic_name[len(topic_name)-1]
        if topic_name == topic_id: exists = True
    
    if not exists: raise Exception("Topic '" + topic_id + "' for project '" + project_id + "' does not exist!")
    
    publisher = pubsub_v1.PublisherClient()

    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    topic_path = publisher.topic_path(project_id, topic_id)
    #if verbose: print("topic_path: ", topic_path)
    # topic_path:  projects/data-platform-2024/topics/raw_streaming

    # Create a data packet.
    # Note that argument "source" is optional metadata that can be encoded into the packet and should ideally be the REGION for the publisher.
    data_packet = create_data_packet(channels=5, source=region)
    if verbose: print(data_packet)
    # {"datetime_created":"2024-09-01T15:37:50.639435+00:00","unix_ms":1725219470000.0,"source":"api_gcp_pub-sub.py","payload":[-8.334515e-39,-3.249203e38,1.0373193e-38,1.98253e38,7.008128e-39]}

    # Create custom metadata as a dictionary
    custom_meta_content = {
        'business': 'Mechatronic Solutions LLC',
        'latitude': 40.44127,
        'longitude': -76.12276,
    }
    # NOTE:  All attributes being published to Pub/Sub must be sent as text strings, 
    #        and the attr argument passed to .publish() must be a string, NOT a dictionary. 
    # https://cloud.google.com/pubsub/docs/samples/pubsub-publish-custom-attributes
    custom_meta_content = json.dumps(custom_meta_content)

    # When you publish a message, the client returns a future.  timeout=600 s is default
    # This method may block if LimitExceededBehavior.BLOCK is used in the flow control settings.
    # pubsub_v1.publisher.exceptions.MessageTooLargeError: If publishing the message would exceed the max size limit on the backend.
    # NOTE: The attrs .publish() argument does NOT accept a dictionary for the metadata (the documentation is incorrect). 
    # https://cloud.google.com/pubsub/docs/samples/pubsub-publisher-retry-settings
    # https://cloud.google.com/pubsub/docs/publisher
    try: 
        future = publisher.publish(topic=topic_path, data=data_packet, attrs=custom_meta_content)
    except Exception as e:
        print("ERROR: " + str(e))
        print(future.result())
        return False, None
    
    # print("msg #: ", future.result())
    return True, future.result()


if __name__ == '__main__':
  pass


  # ---------------------------------------------------------------------------
  # Check that ADC credentials exist for a project & get OS environment variables

  print("\nsavvy_get_os(): " + savvy_get_os() + "")

  script_running_locally = gcp_json_credentials_exist()
  print("\ngcp_json_credentials_exist(): " + str(script_running_locally) + "")

  # The Google Run Jobs argument "--set-env-vars=" sets the environment variable GCP_RUN_JOBS_REGION to the region the script is running in.
  # If not running within Google Run Jobs (e.g. locally, it is set to the default "us-east4")
  gcp_run_jobs_region = os.environ.get("GCP_RUN_JOBS_REGION","us-east4")
  print("GCP_RUN_JOBS_REGION: " + gcp_run_jobs_region)
  if gcp_run_jobs_region == "": raise Exception("GCP_RUN_JOBS_REGION environment variable not set.")

  # Allow environment variables to override global project constants
  PROJECT_ID = os.environ.get("GCP_PROJECT_ID",PROJECT_ID)
  TOPIC_ID = os.environ.get("GCP_TOPIC_ID",TOPIC_ID)

  print("COMPUTERNAME: " + os.environ.get("COMPUTERNAME","")+ "\n")


  if script_running_locally:
    # This script is running locally, either directly or from within a Docker container, but not via Google Run Jobs.

    # Publish a message every 2 minutes (120 seconds).
    # (simulates Scheduler Jobs running and executing a Google Run Jobs running this script)

    while True:
        t_loop_start = perf_counter()

        send_result, msg_no = send_data_packet_to_gcp_pub(project_id=PROJECT_ID, topic_id=TOPIC_ID, region=gcp_run_jobs_region, verbose=True)
        if not send_result: 
            raise Exception("Error sending data packet to " + PROJECT_ID + " | " + TOPIC_ID)
        else:
            print("Message # " + str(msg_no) + " successfully sent the data packet for project_id " + PROJECT_ID + ", topic_id " + TOPIC_ID + "")

        #t = randint(30,90)
        t = 120        # Wait time in seconds between message publishing
        print("Next message publish in " + str(t) + " sec..\n")
        sleep(t)     # wait / pause / sleep for t seconds

        t_loop_elapsed = perf_counter() - t_loop_start
        print("Loop time " + str(round(t_loop_elapsed,1)) + " sec\n")

  else:
    # gcp_json_credentials_exist() == False
    # This script is running from a Docker container via Google Run Jobs.

    # Send data packet to to GCP Pub/Sub once and then exit
    send_result, msg_no = send_data_packet_to_gcp_pub(project_id=PROJECT_ID, topic_id=TOPIC_ID, region=gcp_run_jobs_region, verbose=True)
    if not send_result: 
        raise Exception("Error sending data packet to " + PROJECT_ID + " | " + TOPIC_ID + "\n")
    else:
        print("Message # " + str(msg_no) + " successfully sent the data packet for project_id " + PROJECT_ID + ", topic_id " + TOPIC_ID + " with ack\n")



  # ---------------------------------------------------------------------------
