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

rem https://console.cloud.google.com/billing
rem Edit the billing account number below to be your Google Billing Account No:
rem SET GCP_BILLING_ACCOUNT=0X0X0X-0X0X0X-0X0X0X
echo GCP_BILLING_ACCOUNT: %GCP_BILLING_ACCOUNT%

rem Define Google Pub/Sub topic and subscription IDs
rem SET GCP_PUBSUB_TOPIC=streaming_data_packet_topic
echo GCP_PUBSUB_TOPIC: %GCP_PUBSUB_TOPIC%
rem SET GCP_PUBSUB_SUBSCRIPTION=streaming_data_packet_subscription
echo GCP_PUBSUB_SUBSCRIPTION: %GCP_PUBSUB_SUBSCRIPTION%


rem Docker image names
rem SET GCP_IMAGE_PUB=data-platform-pub
echo GCP_IMAGE_PUB: %GCP_IMAGE_PUB%
rem SET GCP_IMAGE_SUB=data-platform-sub
echo GCP_IMAGE_SUB: %GCP_IMAGE_SUB%

rem Google Artifacts Registry repository
rem SET GCP_REPOSITORY=repo-data-platform
echo GCP_REPOSITORY: %GCP_REPOSITORY%

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


echo.
echo Review the settings listed above carefully.
echo This batch file will cleanup a GCP Project with the above settings (check them carefully).  
echo Note that simply deleting the project '%GCP_PROJ_ID%' will delete everything except the billing account.
echo Press ENTER to continue, or CTRL-C to abort so you can edit this file '%~n0%~x0'.
pause

rem Pause the Google Cloud Scheduler Jobs
rem gcloud scheduler jobs pause SCHEDULER_JOB_NAME --location=SCHEDULER_REGION
CALL gcloud scheduler jobs pause data-platform-pub-run-job --location=us-east4
CALL gcloud scheduler jobs pause data-platform-sub-run-job --location=us-east4

rem List Scheduler Jobs
rem gcloud scheduler jobs list --location=REGION
CALL gcloud scheduler jobs list --location=%GCP_REGION%


rem Delete any existing Scheduler Jobs
echo Deleting any existing Scheduler Jobs by name..
rem gcloud scheduler jobs delete SCHEDULER_JOB_NAME --location=REGION --quiet
CALL gcloud scheduler jobs delete %GCP_RUN_JOB_PUB% --location=%GCP_REGION% --quiet
CALL gcloud scheduler jobs delete %GCP_RUN_JOB_SUB% --location=%GCP_REGION% --quiet
echo.


rem List Scheduler Jobs
rem gcloud scheduler jobs list --location=REGION
CALL gcloud scheduler jobs list --location=%GCP_REGION%


rem List the Cloud Run Jobs by JOB URI
CALL gcloud run jobs list --uri

rem Delete the Cloud Run Jobs if they exist
rem gcloud run jobs delete JOB_NAME --region=REGION --quiet
CALL gcloud run jobs delete %GCP_RUN_JOB_PUB% --region=%GCP_REGION% --quiet
CALL gcloud run jobs delete %GCP_RUN_JOB_SUB% --region=%GCP_REGION% --quiet

rem List the Cloud Run Jobs by JOB URI
CALL gcloud run jobs list --uri

rem List Docker images in Google Artifacts Registry
echo.
echo Docker images in the Google Artifacts Registry %GCP_REGION% repository %GCP_REPOSITORY%:
rem gcloud artifacts docker images list LOCATION-docker.pkg.dev/PROJECT/REPOSITORY --include-tags
CALL gcloud artifacts docker images list %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY% --include-tags

echo.
echo Press RETURN to delete the following Docker images in the Google Artifacts repository %GCP_REPOSITORY%:
echo 	%GCP_IMAGE_PUB%
echo 	%GCP_IMAGE_SUB%
echo Or do CTRL-C to abort.
pause

rem Delete a Docker image in Google Artifacts Registry
rem gcloud artifacts docker images delete IMAGE
@echo on
CALL gcloud artifacts docker images delete %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY%/%GCP_IMAGE_PUB% --quiet
CALL gcloud artifacts docker images delete %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY%/%GCP_IMAGE_SUB% --quiet
@echo off

echo.
echo Press RETURN to delete BigQuery dataset and table.  CTRL-C to abort.
pause

rem List tables 
rem bq ls projectId:datasetId
echo.
echo BigQuery tables for %GCP_PROJ_ID%:%BQ_DATASET_ID%:
CALL bq ls %GCP_PROJ_ID%:%BQ_DATASET_ID%


rem Remove (rm) a table
rem bq rm -f -t project_id:dataset:table_id --quiet
@echo on
CALL bq rm -f --quiet -t %GCP_PROJ_ID%:%BQ_DATASET_ID%:%BQ_TABLE_ID%
@echo off

rem List tables 
rem bq ls projectId:datasetId
echo.
echo BigQuery tables for %GCP_PROJ_ID%:%BQ_DATASET_ID%:
CALL bq ls %GCP_PROJ_ID%:%BQ_DATASET_ID%

rem Delete a dataset and all of its tables (-r), with no confirmation (-f)
rem bq rm -r -f projectId:datasetId
@echo on
CALL bq rm -r -f --quiet %GCP_PROJ_ID%:%BQ_DATASET_ID%
@echo off

rem Delete the project
@echo on
CALL gcloud projects delete %GCP_PROJ_ID% --quiet
@echo off

rem Show project
@echo on
CALL gcloud projects list
@echo off

ENDLOCAL


echo.
echo This batch file has ended normally (no errors).  
