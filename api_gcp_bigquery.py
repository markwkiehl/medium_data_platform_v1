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
Google BigQuery


https://cloud.google.com/bigquery/docs/reference/libraries
https://cloud.google.com/python/docs/reference/bigquery/latest


"""


# pip install --upgrade google-cloud-bigquery
# pip install --upgrade google-cloud-bigquery-storage
from google.cloud import bigquery



def gcp_bq_dataset_exists(project_id=None, dataset_id=None, verbose=False):
    """
    Returns True if the dataset 'dataset_id' exists.
    
    source: https://cloud.google.com/bigquery/docs/listing-datasets#check-dataset-exists
    """
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound

    if project_id is None: raise Exception("Argument project_id not passed as argument")

    if dataset_id is None: raise Exception("Argument dataset_id not passed as argument")
    if ":" in dataset_id: raise Exception("Argument dataset_id has the ':' character. ")
    if "." in dataset_id: raise Exception("Argument dataset_id has the '.' character. ")
    if "-" in dataset_id: raise Exception("Argument dataset_id is invalid.  The '-' character is invalid")

    proj_ds_path = project_id + "." + dataset_id
    if verbose: print("proj_ds_path:" + proj_ds_path)

    client = bigquery.Client(project=project_id)

    try:
        client.get_dataset(proj_ds_path)  # Make an API request.
        if verbose: print("Dataset {} already exists".format(proj_ds_path))
        return True
    except NotFound:
        if verbose: print("Dataset {} is not found or IAM permissions are insufficient.".format(proj_ds_path))
        # Error 403 when permissions are insufficient (but could be other error)
        return False


def gcp_bq_table_exists(project_id=None, dataset_id=None, table_id=None, verbose=False):
    """
    Returns True if the dataset 'dataset_id' and table name 'table_id' exists.
    
    source: Mark W Kiehl / Mechatronic Solutions LLC
    """

    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound

    if project_id is None: raise Exception("Argument project_id not passed as argument")

    if dataset_id is None: raise Exception("Argument dataset_id not passed as argument")
    if ":" in dataset_id: raise Exception("Argument dataset_id has the ':' character. ")
    if "." in dataset_id: raise Exception("Argument dataset_id has the '.' character. ")
    if "-" in dataset_id: raise Exception("Argument dataset_id is invalid.  The '-' character is invalid")

    if table_id is None: raise Exception("Argument table_id not passed as argument")

    proj_ds_path = project_id + "." + dataset_id
    if verbose: print("proj_ds_path:" + proj_ds_path)

    table_path = project_id + "." + dataset_id + "." + table_id
    if verbose: print("table_path:" + table_path)

    # Added project=project_id 20240923
    client = bigquery.Client(project=project_id)

    try:
        client.get_dataset(proj_ds_path)  # Make an API request.
        if verbose: print("Dataset {} exists".format(proj_ds_path))
    except NotFound:
        if verbose: print("Dataset {} is not found or IAM permissions are insufficient.".format(proj_ds_path))
        # Error 403 when permissions are insufficient (but could be other error)
        return False

    try:
        client.get_table(table_path)  # Make an API request.
        if verbose: print("Table {} exists".format(table_path))
        return True
    except NotFound:
        if verbose: print("Table {} is not found or IAM permissions are insufficient.".format(table_path))
        # Error 403 when permissions are insufficient (but could be other error)
        return False



def gcp_bq_insert(project_id=None, dataset_id=None, table_id=None, verbose=False):
    """
    Returns True if the synthetic data generated was succcessfully inserted
    into the BigQuery table `data-platform-v1-5.ds_data_platform.tbl_pubsub`.
    """

    from google.cloud import bigquery
    import numpy as np
    from datetime import datetime, timezone
    from time import mktime

    if project_id is None: raise Exception("Argument project_id not passed as argument")
    if dataset_id is None: raise Exception("Argument dataset_id not passed as argument")
    if ":" in dataset_id: raise Exception("Argument dataset_id has the ':' character. ")
    if "." in dataset_id: raise Exception("Argument dataset_id has the '.' character. ")
    if "-" in dataset_id: raise Exception("Argument dataset_id is invalid.  The '-' character is invalid")

    if table_id is None: raise Exception("Argument table_id not passed as argument")
    if ":" in table_id or "." in table_id: raise Exception("Argument table_id passed an invalid character such as ':' or '.'.  Format is 'table_id'")

    client = bigquery.Client(project=project_id)

    # ds_data_platform
    table_ref = client.dataset(dataset_id).table(table_id)
    if verbose:
        print("table_ref.path:", table_ref.path)
        print("table_ref.project:", table_ref.project)
        #table_ref.path: /projects/data-platform-v1-5/datasets/ds_data_platform/tables/tbl_pubsub
        #table_ref.project: data-platform-v1-5

    """
    Column Name          Data Type    Description

    pub_region           STRING       Google Run Jobs location/region
    datetime_created     TIMESTAMP    When the data was created in UTC
    unix_ms              INT64        When the data was created in Unix time
    Channel_1            FLOAT64
    Channel_2            FLOAT64
    Channel_3            FLOAT64
    Channel_4            FLOAT64
    Channel_5            FLOAT64
    """

    # legacy streaming API approach (not the storage write API for streaming and batch writing data into BigQuery)
    # the data needs to be formatted as an array of JSON objects

    # b'{"datetime_created": "2024-09-17T11:10:57.097792+0000", "unix_ms": 1726585857000.0, "source": "api_gcp_pub_sub.py", "payload": "[0.1726585857, 0.1718020096510774, 0.20850539076573452, 0.8513090904333334, 3.4531717140000002]"}'

    """
    rows_to_insert = [
        {'column1': 'value1', 'column2': 'value2'},
        {'column1': 'value3', 'column2': 'value4'},
    ]

    row1 = {'col1': 1, 'col2': 'foo', 'col3': '2024-02-04'}
    row2 = {'col1': 2, 'col2': 'bar', 'col3': '2024-02-10'}
    rows_to_insert = [row1, row2]
    
        
    """
    datetime_created = datetime.now(tz=timezone.utc)
    # Required Timestamp format is:  YYYY-MM-DD HH:MM[:SS[.SSSSSS]]
    # Value stored after insert: 2024-09-19 00:11:24.283817 UTC

    unix_ms = mktime(datetime_created.timetuple()) * 1000.0

    row1 = {'pub_region': 'us-east4', 
            'datetime_created': datetime_created.strftime("%Y-%m-%dT%H:%M:%S.%f"), 
            'unix_ms': unix_ms,
            'msg_trip_s': float(np.random.uniform(0.0, 2.9)),
            'msg_proc_s': float(np.random.uniform(3.0, 69.0)),
            'Channel_1': float(np.random.uniform(-1.18E-38, +1.18E-38)),
            'Channel_2': float(np.random.uniform(-1.18E-38, +1.18E-38)),
            'Channel_3': float(np.random.uniform(-1.18E-38, +1.18E-38)),
            'Channel_4': float(np.random.uniform(-1.18E-38, +1.18E-38)),
            'Channel_5': float(np.random.uniform(-1.18E-38, +1.18E-38)),
            }
    rows_to_insert = [row1]

    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        print('Errors:', errors)
        return False
    else:
        if verbose: print('Data streamed to BigQuery successfully.')
        return True


def gcp_bq_row_exists(project_id=None, dataset_id=None, table_id=None, unix_ms=None, pub_region=None, verbose=False):
    """
    Returns True if a record matching unix_ms and pub_region exists.

    """

    if project_id is None: raise Exception("Argument project_id has not been passed")
    if dataset_id is None: raise Exception("Argument data_set has not been passed")
    if table_id is None: raise Exception("Argument table_id has not been passed")
    if unix_ms is None: raise Exception("Argument unix_ms has not been passed")
    if pub_region is None: raise Exception("Argument pub_region has not been passed")

    from google.cloud import bigquery
    from time import sleep

    # Construct a BigQuery client object.
    client = bigquery.Client(project=project_id)

    sql = "SELECT unix_ms,pub_region"
    sql += " FROM `" + project_id + "." + dataset_id + "." + table_id + "`"
    sql += " WHERE unix_ms=" + str(unix_ms) + " AND pub_region='" + pub_region + "'"
    sql += " ORDER BY unix_ms;"
    if verbose: print(sql)

    # Execute a batch query.
    job_config = bigquery.QueryJobConfig(
        # Run at batch priority, which won't count toward concurrent rate limit.
        priority=bigquery.QueryPriority.BATCH
    )
    # Start the query, passing in the extra configuration.
    query_job = client.query(sql, job_config=job_config)  # Make an API request.

    # Check on the progress by getting the job's updated state. Once the state
    # is `DONE`, the results are ready.
    query_job = client.get_job(
        query_job.job_id, 
        location=query_job.location
    )  # Make an API request.

    # Note: you can specify a callback rather than using a while loop.
    # query_job.add_done_callback()

    while not query_job.done():
    #while(query_job.state != 'DONE'):
        print("Query job " + str(query_job.job_id) + " is in state " + query_job.state + "")
        sleep(2)

    rows = query_job.result()
    #print("rows.max_results:", rows.max_results)        # The maximum number of results to fetch
    #print("rows.total_rows:", rows.total_rows)          # The total number of rows in the table or query results
    if rows.total_rows > 1: print("WARNING: " + str(rows.total_rows-1) + " duplicate records found!")
    if rows.total_rows > 0:
        return True
    else:
        return False





def gcp_bq_query_db(project_id=None, dataset_id=None, table_id=None, batch_query=True, verbose=False):
    """
    Template for BigQuery query
    
    https://cloud.google.com/bigquery/docs/reference/libraries#use
    https://cloud.google.com/python/docs/reference/bigquery/latest#example-usage
    https://cloud.google.com/bigquery/docs/introduction-sql#changing_from_the_default_dialect
    https://cloud.google.com/bigquery/docs/running-queries#batch
    

    
    BigQuery supports two SQL dialects: standard SQL and legacy SQL. 
    Standard SQL is preferred for querying data stored in BigQuery because it’s compliant with the ANSI SQL 2011 standard.

    When you run a SQL query in BigQuery, it automatically creates, schedules and runs a query job. 
    BigQuery runs query jobs in two modes: interactive (default) and batch.
        - Interactive (on-demand) queries are executed as soon as possible, and these queries count towards concurrent rate limit and daily limit.
        - Batch queries are queued and started as soon as idle resources are available in the BigQuery shared resource pool, which usually occurs within a few minutes. 
          Batch queries don’t count towards your concurrent rate limit. 

    """

    from google.cloud import bigquery
    from time import sleep

    if project_id is None: raise Exception("Argument project_id has not been passed")
    if dataset_id is None: raise Exception("Argument data_set has not been passed")
    if table_id is None: raise Exception("Argument table_id has not been passed")

    # Construct a BigQuery client object.
    client = bigquery.Client(project=project_id)

    sql = "SELECT unix_ms, pub_region, datetime_created, msg_trip_s, msg_proc_s"
    sql += " FROM `" + project_id + "." + dataset_id + "." + table_id + "`"
    sql += " ORDER BY unix_ms;"
    if verbose: print(sql)


    # Execute an interactive query, or batch query.
    # (see also continuous query: https://cloud.google.com/bigquery/docs/continuous-queries)

    if batch_query:
        job_config = bigquery.QueryJobConfig(
            # Run at batch priority, which won't count toward concurrent rate limit.
            priority=bigquery.QueryPriority.BATCH
        )
        # Start the query, passing in the extra configuration.
        query_job = client.query(sql, job_config=job_config)  # Make an API request.
        #print("query_job.location:", query_job.location)        # us-east4

        # Check on the progress by getting the job's updated state. Once the state
        # is `DONE`, the results are ready.
        query_job = client.get_job(
            query_job.job_id, 
            location=query_job.location
        )  # Make an API request.

        # Note: you can specify a callback rather than using a while loop.
        # query_job.add_done_callback()

        while not query_job.done():
        #while(query_job.state != 'DONE'):
            print("Query job " + str(query_job.job_id) + " is in state " + query_job.state + "")
            sleep(2)

        rows = query_job.result()

    else:
        # use query_and_wait to run queries for faster performance with small results.
        rows = client.query_and_wait(query=sql)  # Make an API request.


    #print("rows.job_id:", rows.job_id)      
    #print("rows.query_id:", rows.query_id)
    #print("rows.location:", rows.location)
    #print("rows.path:", rows.path)
    #print("rows.max_results:", rows.max_results)        # The maximum number of results to fetch
    #print("rows.total_rows:", rows.total_rows)          # The total number of rows in the table or query results
    #rows.job_id: job_zDWxvyyC7JghlpuvBaMvD36UkesP
    #rows.query_id: job_zDWxvyyC7JghlpuvBaMvD36UkesP
    #rows.location: us-east4
    #rows.path: None
    #rows.max_results: None
    #rows.total_rows: 5
    
    print(str(rows.total_rows) + " rows")
    print("\t" + "unix_ms" + "\t\t" + "pub_region" + "\t" + "datetime_created" + "\t\t\t" + "msg_trip_s" + "\t" + "msg_proc_s")
    for row in rows:
        # Row values can be accessed by field name or index.
        #print(type(row), row)     # <class 'google.cloud.bigquery.table.Row'> Row((1726753885000, 'us-east4'), {'unix_ms': 0, 'pub_region': 1})
        print("\t" + str(row['unix_ms']) + "\t" + str(row['pub_region']) + "\t" + str(row['datetime_created']) + "\t" + str(round(row['msg_trip_s'],1)) + "\t\t" + str(round(row['msg_proc_s'],3)))

    # ANOTHER METHOD
    """
    QUERY = (
        'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` '
        'WHERE state = "TX" '
        'LIMIT 100')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    for row in rows:
        print(row.name)

    """

    """
    google.api_core.exceptions.Forbidden: 403 POST https://bigquery.googleapis.com/bigquery/v2/projects/data-platform-v1-5/queries?prettyPrint=false: Access Denied: Project data-platform-v1-5: User does not have bigquery.jobs.create permission in project data-platform-v1-5.

    """



if __name__ == '__main__':

    print()

    # ---------------------------------------------------------------------------
    # CONGIGURE THE FOLLOWING PROJECT CONSTANTS: 

    PROJECT_ID = "data-platform-v1-6"
    DATASET_ID = "ds_data_platform"
    TABLE_ID = "tbl_pubsub"

    # ---------------------------------------------------------------------------

    # Verify that the dataset exists
    #print("gcp_bq_dataset_exists(" + DATASET_ID + "): ", gcp_bq_dataset_exists(project_id=PROJECT_ID, dataset_id=DATASET_ID))
    #if not gcp_bq_dataset_exists(project_id=PROJECT_ID, dataset_id=DATASET_ID): raise Exception("Dataset ID not found: " + DATASET_ID)

    # Verify that the dataset & table exists
    #print("gcp_bq_table_exists(" + DATASET_ID + "): ", gcp_bq_table_exists(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, verbose=False))
    if not gcp_bq_table_exists(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, verbose=False): raise Exception("Table not found: " + TABLE_ID)

    # Insert synthetic data into the Google BigQuery table 
    #print("gcp_bq_insert(): ", gcp_bq_insert(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID))

    # Execute a batch query
    gcp_bq_query_db(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, batch_query=True)

    # Check if a particular row exists in the table by columns: unix_ms and pub_region
    #print("\ngcp_bq_row_exists(): ", gcp_bq_row_exists(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, unix_ms=1726757043000, pub_region="us-east4"))


    # ---------------------------------------------------------------------------
