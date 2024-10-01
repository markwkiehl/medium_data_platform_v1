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

Subscriber to the Google Pub/Sub message service

"""

# pip install numpy
# pip install --upgrade google-cloud-pubsub

# pip install --upgrade google-cloud-bigquery
from google.cloud import bigquery

from api_gcp_pub_sub import gcp_json_credentials_exist, gcp_pubsub_get_subscriptions
from api_gcp_bigquery import gcp_bq_table_exists, gcp_bq_row_exists
from savvy_os import savvy_get_os
import os

# ---------------------------------------------------------------------------
# CONGIGURE THE FOLLOWING PROJECT CONSTANTS: 

PROJECT_ID = "data-platform-v1-6"
SUBSCRIPTION_ID = "streaming_data_packet_subscription"

# BigQuery      data-platform-v1-5.ds_data_platform.tbl_pubsub
DATASET_ID = "ds_data_platform"
TABLE_ID = "tbl_pubsub"

# PROJECT_ID,topic_id,dataset_id,table_id
# ---------------------------------------------------------------------------



def gcp_write_pubsub_msg_to_bq(project_id=None, dataset_id=None, table_id=None, message=None, verbose=True):
    """"
    Returns True if successful.

    Decodes the Google Pub/Sub message and writes inserts a new record into
    the Google BigQuery database.

    """

    from datetime import datetime, timezone
    import json
    from google.cloud import bigquery
    import numpy as np
    from time import mktime, perf_counter

    if project_id is None: raise Exception("Argument project_id has not been passed")
    if dataset_id is None: raise Exception("Argument data_set has not been passed")
    if table_id is None: raise Exception("Argument table_id has not been passed")

    if verbose:
        print("message.data:", message.data)
        print("ordering_key:", message.ordering_key)
        print("attributes:", message.attributes)

    t_start_sec = perf_counter()
    # Get the metadata within the message
    attrs = message.attributes['attrs']     # <class 'str'>
    # attrs: {"business":"Mechatronic Solutions LLC","latitude":40.44127,"longitude":-76.12276,"unix_ms":1679828219121,"time":"2023-03-26T10:58:59+0000", "source"}
    # Convert the string to a Python dictionary
    attrs = json.loads(attrs)
    #print("attrs[business]:", attrs['business'])

    # deserializes JSON in message.data to Python objects
    try:
        data = json.loads(message.data)     
    except json.JSONDecodeError as e:
        raise Exception(e)
    # data is now a dictionary
    
    datetime_created = data['datetime_created']
    datetime_created = datetime.strptime(datetime_created, "%Y-%m-%dT%H:%M:%S.%f%z")
    #print("datetime_created:", datetime_created)    
    
    # Calculate the message send/receive time
    unix_ms_now = mktime(datetime.now(tz=timezone.utc).timetuple()) * 1000
    elapsed_ms = unix_ms_now - data['unix_ms']
    # Extract the time in unix_ms and convert to a Python date object
    unix_ms = data['unix_ms']
    #print("unix_ms:", unix_ms, "\t", datetime.fromtimestamp(unix_ms/1000.0, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f%z'))
    
    # Deserialize the JSON string holding the list (JSON array) of floating point values
    payload = json.loads(data['payload'])
    #if verbose: print(str(len(payload)) + " channels of data:")
    #for i in range(0,len(payload)):
    #    if verbose: print("\tCh " + str(i) + "\t" + str(payload[i]))

    pub_region = data['pub_region']
    #print("pub_region: " + pub_region)

    # Report the message send/receive time
    print("Message send/receive time: " + str(round(elapsed_ms/1000.0,1)) + " sec round trip including Scheduler Run Jobs interval delay")

    # Report the script execution time
    t_elapsed_sec = perf_counter() - t_start_sec
    print("Callback message processing elapsed time " + str(round(t_elapsed_sec,3)) + " sec")

    # Store the message data in Google BigQuery only if the record doesn't already exist.
    if gcp_bq_row_exists(project_id=project_id, dataset_id=dataset_id, table_id=table_id, unix_ms=unix_ms, pub_region=pub_region):
        print("WARNING:  The record already exists in table '" + table_id + "' and therefore it will not be added.")
        return False
    else:
        client = bigquery.Client()

        table_ref = client.dataset(dataset_id).table(table_id)

        row = {'pub_region': 'us-east4', 
                'datetime_created': datetime_created.strftime("%Y-%m-%dT%H:%M:%S.%f"), 
                'unix_ms': unix_ms,
                'msg_trip_s': elapsed_ms/1000.0,
                'msg_proc_s': t_elapsed_sec,
                }
        for i in range(0,len(payload)):
            row["Channel_" + str(i+1)] = payload[i]
        rows_to_insert = [row]
        #print("row:", row)  # {'pub_region': 'us-east4', 'datetime_created': '2024-09-20T11:31:38.520109', 'unix_ms': 1726846298000.0, 'Channel_1': 0.1726846298, 'Channel_2': 0.17182766645607023, 'Channel_3': 0.20854329490139709, 'Channel_4': 0.8513872227333332, 'Channel_5': 3.453692596}
    
        errors = client.insert_rows_json(table_ref, rows_to_insert)
        if errors:
            print('Errors:', errors)
            return False
        else:
            if verbose: print('Data inserted into the BigQuery table from the last message successfully.')
            return True



def gcp_pubsub_get_pull_subscription_message(project_id=None, subscription_id=None, timeout_s=600.0, verbose=False):
    """
    Pull messages from Google Pub/Sub via a subscription, acknowledge the message using the callback(),
    and write the message data to BigQuery if the table specified by table_id exist.

    Note that the callback() is customized for decoding the message and calls gcp_write_pubsub_msg_to_bq() if table_id exists.
    
    Uses the global constants: project_id,topic_id,dataset_id,table_id

    The best Google example:  https://cloud.google.com/python/docs/reference/pubsub/latest
    Stackoverflow topic:  https://stackoverflow.com/questions/tagged/google-cloud-pubsub

    """
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1
    from google.cloud.pubsub_v1.subscriber import exceptions as sub_exceptions

    # pip install --upgrade google-cloud-bigquery
    # from google.cloud import bigquery

    if project_id is None: raise Exception("Argument project_id not passed to the function.")
    if subscription_id is None: raise Exception("Argument subscription_id not passed to the function.")

    subscriber = pubsub_v1.SubscriberClient()

    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    # WARNING:  The callback below that uses <class 'google.cloud.pubsub_v1.subscriber.message.Message'> 
    # doesn't return a message greater than 50 bytes:
    #   def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    # A callback(message) however does fetch an entire message. 

    def callback(message):
        """
        This function is called when a message is received.
        The message will have the properties of:
            message.data        (this is the data package)
            message.attributes
        """        

        # Use `ack_with_response()` instead of `ack()` to get a future that tracks
        # the result of the acknowledge call. When exactly-once delivery is enabled
        # on the subscription, the message is guaranteed to not be delivered again
        # if the ack future succeeds.
        #message.ack()
        ack_future = message.ack_with_response()

        try:
            # Block on result of acknowledge call.
            # When `timeout` is not set, result() will block indefinitely, unless an exception is encountered first.
            ack_future.result(timeout=5.0)      # was 5.0
            print("\nAck for message # " + str(message.message_id) + " successful.")
        except sub_exceptions.AcknowledgeError as e:
            print("\nAck for message # " + str(message.message_id) + " failed with error " + str(e.error_code))

        if gcp_bq_table_exists(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, verbose=False):
            # The table exists.  Write the message data to the BigQuery table TABLE_ID
            if not gcp_write_pubsub_msg_to_bq(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, message=message):
                raise Exception("gcp_write_pubsub_msg_to_bq() error")
        else:
            # The BigQuery table doesn't exist.  Just print out the data. 
            print("message.data:", message.data)
            print("ordering_key:", message.ordering_key)
            print("attributes:", message.attributes)


    # Asynchronously start receiving messages on a given subscription.
    # Starts a background thread to begin pulling messages from a Pub/Sub subscription and scheduling them to be processed using the provided callback.
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print("\nListening for messages from " + subscription_path + "")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely, unless an exception is encountered first.
            # timeout indicates how long you want the subscriber to receive messages. 
            streaming_pull_future.result(timeout=timeout_s)
        except TimeoutError:
            print("Message listening stopped. The timeout of " + str(timeout_s) + "s was reached.")
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.
        except KeyboardInterrupt:
            print("Keyboard interrupt stopped script")
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.
        except Exception as e:
            print("ERROR: " + str(e))
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.

        # Will not reach here until timeout_s has elapsed


    # When exactly-once delivery is enabled on the subscription, 
    # after an Ack, this error can happen:  
    #   AcknowledgeError when lease-modacking a message.
    #   google.cloud.pubsub_v1.subscriber.exceptions.AcknowledgeError: None AcknowledgeStatus.INVALID_ACK_ID
    # This indicates a failure not in acknowledging the message, but in extending its ack deadline.
    # This error message may happen if the ack and a lease modack go back to the server at around the same time and the ack is processed first. In such a case, the modack is no longer valid because the ack on the message has occurred. The error does not mean that your message was not acknowledged.
    # Reducing the ack timeout from 60 to 5 seconds seems to have helped.  ack_future.result(timeout=5.0)



if __name__ == '__main__':
    pass

    # Allow environment variables to override global project constants
    PROJECT_ID = os.environ.get("GCP_PROJECT_ID",PROJECT_ID)
    SUBSCRIPTION_ID = os.environ.get("GCP_SUBSCRIPTION_ID",SUBSCRIPTION_ID)
    DATASET_ID = os.environ.get("GCP_DATASET_ID",DATASET_ID)
    TABLE_ID = os.environ.get("GCP_TABLE_ID",TABLE_ID)

    # timeout_s indicates how long the subscriber should receive messages. 
    timeout_s = 5.0        

    # ---------------------------------------------------------------------------
    # Check that credentials exist for a project

    print("\nsavvy_get_os(): " + savvy_get_os() + "")

    script_running_locally = gcp_json_credentials_exist()
    print("\ngcp_json_credentials_exist(): " + str(script_running_locally) + "")

    if script_running_locally:
        # This script is running locally, either directly or from within a Docker container, but not via Google Run Jobs.

        # Simulate a Schedule Run Job that executes every 59 seconds
        from time import sleep, perf_counter

        subscriptions = gcp_pubsub_get_subscriptions(project_id=PROJECT_ID, verbose=False)
        if len(subscriptions) == 0: raise Exception("No subscriptions found for project_id " + PROJECT_ID)
        
        while True:
            t_loop_start = perf_counter()

            # Check for subscriptions for subscription_id and process them if they exist
            gcp_pubsub_get_pull_subscription_message(project_id=PROJECT_ID, subscription_id=SUBSCRIPTION_ID, timeout_s=timeout_s, verbose=True)
            
            t = 60      # Sleep duration in seconds
            # ack future timeout is 5.0 seconds
            #t = t - timeout_s - 5.0
            print("Next subscription check in " + str(t) + " sec..")
            sleep(t)     # wait / sleep / pause for t seconds

            t_loop_elapsed = perf_counter() - t_loop_start
            print("Loop time " + str(round(t_loop_elapsed,1)) + " sec")

            # Loop time ~67 sec when no messages are received. 
            # Message send/receive time: ? sec round trip including Scheduler Run Jobs interval delay
            # Callback message processing elapsed time 0.6 to 1.7 sec
    else:
        # gcp_json_credentials_exist() == False
        # This script is running from a Docker container via Google Run Jobs.

        # Pull subscribe with exactly-once message delivery  (read messages for a subscription)
        # https://cloud.google.com/pubsub/docs/exactly-once-delivery#subscribe_with_exactly-once_message_delivery

        # Get the exactly-once message for a subscription
        subscriptions = gcp_pubsub_get_subscriptions(project_id=PROJECT_ID, verbose=False)
        if len(subscriptions) == 0: raise Exception("No subscriptions found for project_id " + PROJECT_ID)
        
        # Check for subscriptions for subscription_id and process them if they exist
        gcp_pubsub_get_pull_subscription_message(project_id=PROJECT_ID, subscription_id=SUBSCRIPTION_ID, timeout_s=timeout_s, verbose=True)

        # Typically the callback processes the message in 0.8 to 1.3 sec (excludes storage actions)
        # Typically the round trip message send/receive is 4.0 to 6.0 sec



