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
Analytics using Pandas & Google BigQuery


"""


# pip install --upgrade google-cloud-bigquery
# pip install --upgrade google-cloud-bigquery-storage
from google.cloud import bigquery


# pip install pandas
# pip install db-dtypes
import pandas as pd

# pip install matplotlib
import matplotlib.pyplot as plt

from api_gcp_bigquery import gcp_bq_table_exists


def get_tbl_data_as_df(project_id=None, dataset_id=None, table_id=None, sql=None, verbose=False):
    from time import sleep

    # Create a BigQuery client
    client = bigquery.Client(project=project_id)

    # Run the query as a batch job
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
        if verbose: print("Query job " + str(query_job.job_id) + " is in state " + query_job.state + "")
        sleep(2)

    #rows = query_job.result()

    # Convert the results to a pandas DataFrame
    df = query_job.to_dataframe()

    return df



if __name__ == '__main__':

    print()

    # ---------------------------------------------------------------------------
    # CONGIGURE THE FOLLOWING PROJECT CONSTANTS: 

    PROJECT_ID = "data-platform-v1-6"
    DATASET_ID = "ds_data_platform"
    TABLE_ID = "tbl_pubsub"

    # ---------------------------------------------------------------------------

    # Verify that the dataset & table exists
    #print("gcp_bq_table_exists(" + DATASET_ID + "): ", gcp_bq_table_exists(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, verbose=False))
    if not gcp_bq_table_exists(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, verbose=False): raise Exception("Table not found: " + TABLE_ID)

    # ---------------------------------------------------------------------------
    # Execute a BigQuery query and import the results into a Pandas dataframe

    from pathlib import Path  

    # Save/ Read Parquet file hereafter rather than executing BigQuery
    path_file = Path(Path.cwd()).joinpath(TABLE_ID + ".parquet")

    # Uncomment line below to cause the data to be read from BigQuery again and saved locally to a Parquet file.
    #if path_file.exists(): path_file.unlink()       

    if not path_file.exists():
        # Query BigQuery to get the data

        sql = "SELECT unix_ms, Channel_1, Channel_2, Channel_3, Channel_4, Channel_5"
        sql += " FROM `" + PROJECT_ID + "." + DATASET_ID + "." + TABLE_ID + "`"
        sql += " ORDER BY unix_ms;"
        print(sql)

        df = get_tbl_data_as_df(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID, sql=sql, verbose=True)
        # UserWarning: BigQuery Storage module not found, fetch data with the REST endpoint instead.
        print(df)

        # Save the dataframe to a Parquet file
        print("Saving dataframe file to: ", path_file.name)
        df.to_parquet(path=path_file, compression='gzip')
        
        del df

    # Read back the datafrom from the Parquet file
    if not path_file.exists(): raise Exception("File doesn't exist: ", path_file)
    print("Reading Parquet file: ", path_file.name)
    df = pd.read_parquet(path=path_file)     

    # Print the DataFrame
    print(df)

    # Get the value for the first row using iloc[0]
    first_row_unix_ms = df['unix_ms'].iloc[0]
    print("first_row_unix_ms:", df['unix_ms'].iloc[0])      # 1727271976000
    print()

    # Subtract the first row value in column 'unix_ms' from every value.
    df['unix_ms'] = df['unix_ms'] - first_row_unix_ms


    #print(df)
    #      unix_ms  Channel_1  Channel_2  Channel_3
    #0           0   0.172727   0.171870   0.208605
    #1      120000   0.172727   0.171870   0.208605
    #2      239000   0.172727   0.171870   0.208605
    #..        ...        ...        ...        ...
    #110  13199000   0.172729   0.171871   0.208607

    # Set column unix_ms as the index
    df.set_index('unix_ms', inplace=True)

    print(df)

    print(df.describe())

    # matplotlib subplots stacked in vertical direction of all five channels
    fig, ax = plt.subplots(df.shape[1], figsize=(10,6), sharex=True)     #sharex synchronizes the x-axis across all plots
    fig.suptitle(PROJECT_ID + "." + DATASET_ID + "." + TABLE_ID)
    i = 0
    for c in df.columns:
        ax[i].plot(df.index, df[c])       # ax[0] is the top plot
        ax[i].title.set_text(c)
        ax[i].tick_params(axis="x", rotation=25, labelsize=6) 
        i += 1
    plt.tight_layout()  # makes the dialog fit the content
    plt.show()
    



    # ---------------------------------------------------------------------------

