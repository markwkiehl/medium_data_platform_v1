@echo off
cls
echo %~n0%~x0
echo.

rem Created by Mechatronic Solutions LLC
rem Mark W Kiehl
rem
rem LICENSE: MIT


rem Batch files: https://steve-jansen.github.io/guides/windows-batch-scripting/
rem Batch files: https://tutorialreference.com/batch-scripting/batch-script-tutorial
rem Scripting Google CLI:  https://cloud.google.com/sdk/docs/scripting-gcloud

rem Verify that CLOUDSDK_PYTHON has already been set permanently for the user by gcp_part1.bat
IF NOT EXIST "%CLOUDSDK_PYTHON%" (
echo ERROR: CLOUDSDK_PYTHON path not found.  %CLOUDSDK_PYTHON%
echo Did you previously run gcp_part1.bat ?
EXIT /B
)


rem Make sure GOOGLE_APPLICATION_CREDENTIALS is not set so that Google ADC flow will work properly.
IF NOT "%GOOGLE_APPLICATION_CREDENTIALS%"=="" (
echo .
echo ERROR: GOOGLE_APPLICATION_CREDENTIALS has been set!
echo GOOGLE_APPLICATION_CREDENTIALS=%GOOGLE_APPLICATION_CREDENTIALS%
echo The environment variable GOOGLE_APPLICATION_CREDENTIALS must NOT be set in order to allow Google ADC to work properly.
echo Press RETURN to unset GOOGLE_APPLICATION_CREDENTIALS, CTRL-C to abort. 
pause
@echo on
SET GOOGLE_APPLICATION_CREDENTIALS=
CALL SETX GOOGLE_APPLICATION_CREDENTIALS ""
@echo off
echo Restart this file %~n0%~x0
EXIT /B
)




SETLOCAL

rem Define the working folder to Google Cloud CLI (gcloud) | Google Cloud SDK Shell
rem derived from the USERPROFILE environment variable.
rem This requires that the Google CLI/SKD has already been installed.
SET PATH_GCLOUD=%USERPROFILE%\AppData\Local\Google\Cloud SDK
IF NOT EXIST "%PATH_GCLOUD%\." (
	echo ERROR: PATH_GCLOUD path not found.  %PATH_GCLOUD%
	echo Did you install Google CLI / SKD? 
	EXIT /B
)
rem echo PATH_GCLOUD: %PATH_GCLOUD%

rem The current working directory for this script should be the same as the Python virtual environment for this project.
SET PATH_SCRIPT=%~dp0
rem echo PATH_SCRIPT: %PATH_SCRIPT%
rem echo CLOUDSDK_PYTHON: %CLOUDSDK_PYTHON%


echo.
echo PROJECT LOCAL VARIABLES:
echo.

rem Next two variables defined earlier
rem echo GCP_PYTHON_VERSION: %GCP_PYTHON_VERSION%


rem import the GCP project constants from file gcp_constants.bat
if EXIST "gcp_constants.bat" (
  for /F "tokens=*" %%I in (gcp_constants.bat) do set %%I
) ELSE (
  echo ERROR: unable to find gcp_constants.bat
  EXIT /B
)


rem ----------------------------------------------------------------------
rem Edit the project variables below

rem set GCP_PROJ_ID=data-platform-v0-0
echo GCP_PROJ_ID: %GCP_PROJ_ID%

rem set GCP_REGION=us-east4
echo GCP_REGION: %GCP_REGION%

rem SET GCP_USER=username@gmail.com
echo GCP_USER: %GCP_USER%

rem SET GCP_SVC_ACT=svc-act-pubsub@%GCP_PROJ_ID%.iam.gserviceaccount.com
SET GCP_SVC_ACT=%GCP_SVC_ACT_PREFIX%@%GCP_PROJ_ID%.iam.gserviceaccount.com
echo GCP_SVC_ACT: %GCP_SVC_ACT%

rem Google Run Jobs
rem SET GCP_RUN_JOB_PUB=data-platform-pub-run-job
echo GCP_RUN_JOB_PUB: %GCP_RUN_JOB_PUB%
rem SET GCP_RUN_JOB_SUB=data-platform-sub-run-job
echo GCP_RUN_JOB_SUB: %GCP_RUN_JOB_SUB%

rem BigQuery
rem SET BQ_DATASET_ID=ds_data_platform
echo BQ_DATASET_ID: %BQ_DATASET_ID%
rem SET BQ_TABLE_ID=tbl_pubsub
echo BQ_TABLE_ID: %BQ_TABLE_ID%


rem ----------------------------------------------------------------------


echo.
echo This batch file will configure Google BigQuery and create a dataset named '%BQ_DATASET_ID%'
echo and a database table named '%BQ_TABLE_ID%', both in the region/location '%GCP_REGION%'.
echo Press ENTER to continue, or CTRL-C to abort so you can edit the file gcp_constants.bat.
pause

echo.
echo Granting permissions/roles to the user-managed service account 
echo and enabling the BigQuery API.
echo A browser window will open and ask you to approve the changes.
echo You may close the browser tab that opens after approval is given.
echo Press RETURN to continue, CTRL-C to abort.
pause
echo.

rem Grant the user-managed service account the roles required for BigQuery
rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/bigquery.dataViewer
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.dataViewer
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.dataViewer
	EXIT /B
)

rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/bigquery.metadataViewer
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.metadataViewer
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.metadataViewer
	EXIT /B
)

rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/bigquery.readSessionUser
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.readSessionUser
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.readSessionUser
	EXIT /B
)

rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/bigquery.user
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.user
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.user
	EXIT /B
)

rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/bigquery.dataOwner
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.dataOwner
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/bigquery.dataOwner
	EXIT /B
)

rem Summarize the roles assigned to the service agent
echo.
echo Roles assigned to %GCP_SVC_ACT%:
rem gcloud projects get-iam-policy PROJECT_ID --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:serviceAccount:svc-act-name@PROJECT_ID.iam.gserviceaccount.com"
CALL gcloud projects get-iam-policy %GCP_PROJ_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:serviceAccount:%GCP_SVC_ACT%"
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects get-iam-policy %GCP_PROJ_ID% --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:serviceAccount:%GCP_SVC_ACT%"
	EXIT /B
)
echo.


rem Enable the BigQuery API
CALL gcloud services enable bigquery.googleapis.com
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud services enable bigquery.googleapis.com
	EXIT /B
)

rem Update local ADC / user-managed service account impersonation
CALL gcloud auth application-default login --impersonate-service-account %GCP_SVC_ACT%
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud auth application-default login --impersonate-service-account %GCP_SVC_ACT% 
	EXIT /B
)

echo.
echo Press RETURN to continue and create a BigQuery dataset and table.  CTRL-C to quit.
pause

rem Delete any dataset and tables that may already exist 
rem Delete a dataset and all of its tables (-r), with no confirmation (-f)
rem bq rm -r -f projectId:datasetId
@echo on
CALL bq rm -r -f --quiet %GCP_PROJ_ID%:%BQ_DATASET_ID%
@echo off


rem Create the dataset
@echo on
CALL bq --location=%GCP_REGION% mk -d --default_table_expiration 86400 --description "dataset for %GCP_PROJ_ID%" %GCP_PROJ_ID%:%BQ_DATASET_ID%
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: bq --location=%GCP_REGION% mk -d --default_table_expiration 86400 --description "dataset for %GCP_PROJ_ID%" %GCP_PROJ_ID%:%BQ_DATASET_ID%
	EXIT /B
)

rem List datasets for a project
echo.
echo Datasets for %GCP_PROJ_ID%:
rem bq ls --format=pretty --project_id=projectId
CALL bq ls --format=pretty --project_id=%GCP_PROJ_ID%


rem Create a new table using SQL CREATE TABLE command with a primary key specified
rem bq query --use_legacy_sql=false "CREATE OR REPLACE TABLE project-id.dataset_name.table_name (column1 STRING,datetime_created TIMESTAMP,column2 INT64,Channel_1  column3,Channel_2, ..,PRIMARY KEY (col1, col2, ..) NOT ENFORCED);"
@echo on
CALL bq query --use_legacy_sql=false "CREATE OR REPLACE TABLE %GCP_PROJ_ID%.%BQ_DATASET_ID%.%BQ_TABLE_ID% (unix_ms INT64 NOT NULL,pub_region STRING NOT NULL,datetime_created TIMESTAMP NOT NULL,msg_trip_s FLOAT64,msg_proc_s FLOAT64,Channel_1  FLOAT64,Channel_2  FLOAT64,Channel_3  FLOAT64,Channel_4  FLOAT64,Channel_5  FLOAT64,PRIMARY KEY (unix_ms, pub_region) NOT ENFORCED);"
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: bq query --use_legacy_sql=false "CREATE OR REPLACE TABLE %GCP_PROJ_ID%.%BQ_DATASET_ID%.%BQ_TABLE_ID% (unix_ms INT64 NOT NULL,pub_region STRING NOT NULL,datetime_created TIMESTAMP NOT NULL,msg_trip_s FLOAT64,msg_proc_s FLOAT64,Channel_1  FLOAT64,Channel_2  FLOAT64,Channel_3  FLOAT64,Channel_4  FLOAT64,Channel_5  FLOAT64,PRIMARY KEY (unix_ms, pub_region) NOT ENFORCED);"
	EXIT /B
)

rem List tables 
rem bq ls projectId:datasetId
echo.
echo BigQuery tables for %GCP_PROJ_ID%:%BQ_DATASET_ID%:
CALL bq ls %GCP_PROJ_ID%:%BQ_DATASET_ID%

rem List the Google Scheduler Jobs
echo.
echo Google Cloud Scheduler Jobs:
@echo on
CALL gcloud scheduler jobs list --location=%GCP_REGION%
@echo off

echo.
echo The BigQuery dataset and table listed above are ready to use.
echo Press ENTER to continue and unpause the Google Cloud Scheduler Jobs
echo so that the Python scrips will begin to write data to the BigQuery table. 
echo Use CTRL-C to abort.
pause


@echo on
CALL gcloud scheduler jobs resume %GCP_RUN_JOB_PUB% --location=%GCP_REGION%
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud scheduler jobs resume %GCP_RUN_JOB_PUB% --location=%GCP_REGION%
	EXIT /B
)

@echo on
CALL gcloud scheduler jobs resume %GCP_RUN_JOB_SUB% --location=%GCP_REGION%
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud scheduler jobs resume %GCP_RUN_JOB_SUB% --location=%GCP_REGION%
	EXIT /B
)

echo.
echo Use the command below to check on the status of generation of rows in table %BQ_TABLE_ID%
@echo on
CALL bq query --use_legacy_sql=false "CREATE OR REPLACE TABLE %GCP_PROJ_ID%.%BQ_DATASET_ID%.%BQ_TABLE_ID% (unix_ms INT64 NOT NULL,pub_region STRING NOT NULL,datetime_created TIMESTAMP NOT NULL,msg_trip_s FLOAT64,msg_proc_s FLOAT64,Channel_1  FLOAT64,Channel_2  FLOAT64,Channel_3  FLOAT64,Channel_4  FLOAT64,Channel_5  FLOAT64,PRIMARY KEY (unix_ms, pub_region) NOT ENFORCED);"
@echo off

ENDLOCAL

echo.
echo This batch file %~n0%~x0 has ended normally (no errors).  
echo Congratulations, you may now continue with the article Part Seven - Google Cloud Analytics.