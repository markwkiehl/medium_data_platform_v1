@echo off
cls
echo %~n0%~x0   version 0.0.0
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

rem https://console.cloud.google.com/billing
rem Edit the billing account number below to be your Google Billing Account No:
rem SET GCP_BILLING_ACCOUNT=0X0X0X-0X0X0X-0X0X0X
rem echo GCP_BILLING_ACCOUNT: %GCP_BILLING_ACCOUNT%

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



rem ----------------------------------------------------------------------


echo.
echo This batch file will configure and run Google Run Jobs and Google Scheduler Jobs 
echo for the Pub/Sub publisher and subscriber Docker images in the Google Artifacts
echo Registry repository named %GCP_REPOSITORY%.
echo Review all of the local variable assignments shown above carefully. 
echo Press ENTER to continue, or CTRL-C to abort.
pause

echo.

echo Granting permissions/roles to the user-managed service account 
echo and enabling the Google Cloud Run and Scheduler APIs.
echo A browser window will open and ask you to approve the changes.
echo.

rem Grant the user-managed service account the roles required for Cloud Run Jobs & Scheduler Jobs
rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/run.invoker
@echo on
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/run.invoker
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/run.invoker
	EXIT /B
)

rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/cloudscheduler.admin
@echo on
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/cloudscheduler.admin
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/cloudscheduler.admin
	EXIT /B
)

rem Enable the Cloud Run API
@echo on
CALL gcloud services enable run.googleapis.com
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: services enable run.googleapis.com
	EXIT /B
)

rem Enable the Google Scheduler API
@echo on
CALL gcloud services enable cloudscheduler.googleapis.com
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: services enable cloudscheduler.googleapis.com
	EXIT /B
)

rem Update local ADC / user-managed service account impersonation
echo.
echo Google user %GCP_USER% must authorize the addition of the roles and enabled APIs.
echo You may close the browser when authorization is complete and then return to this window.
pause
@echo on
CALL gcloud auth application-default login --impersonate-service-account %GCP_SVC_ACT%
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud auth application-default login --impersonate-service-account %GCP_SVC_ACT% 
	EXIT /B
)

rem List the Docker images in a repository and include the tag
echo.
echo Docker images in Google Artifacts repository %GCP_REPOSITORY%:
rem gcloud artifacts docker images list LOCATION-docker.pkg.dev/PROJECT/REPOSITORY --include-tags
CALL gcloud artifacts docker images list %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY% --include-tags
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud artifacts docker images list %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY% --include-tags
	EXIT /B
)

rem Delete the Cloud Run Jobs if they exist
rem gcloud run jobs delete JOB_NAME --region=REGION --quiet
echo.
@echo on
CALL gcloud run jobs delete %GCP_RUN_JOB_PUB% --region=%GCP_REGION% --quiet
CALL gcloud run jobs delete %GCP_RUN_JOB_SUB% --region=%GCP_REGION% --quiet
@echo off
echo Ignore any errors above.


rem Create a Google Cloud Run job from the Docker image for the publisher
rem gcloud run jobs create JOB_NAME --image=IMAGE_URL --region=REGION
rem NOTE:  Removed below the double quotes around GCP_RUN_JOBS_REGION=us-east4
CALL gcloud run jobs create %GCP_RUN_JOB_PUB% --image=%GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY%/%GCP_IMAGE_PUB%:latest --region=%GCP_REGION% --set-env-vars=GCP_RUN_JOBS_REGION=%GCP_REGION% --set-env-vars="GCP_PROJECT_ID=%GCP_PROJ_ID%" --set-env-vars="GCP_TOPIC_ID=%GCP_PUBSUB_TOPIC%"
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: 
	EXIT /B
)

rem Create a Google Cloud Run job from the Docker image for the subscriber
rem gcloud run jobs create JOB_NAME --image=IMAGE_URL --region=REGION
rem NOTE:  Removed below the double quotes around GCP_RUN_JOBS_REGION=us-east4
CALL gcloud run jobs create %GCP_RUN_JOB_SUB% --image=%GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY%/%GCP_IMAGE_SUB%:latest --region=%GCP_REGION% --set-env-vars=GCP_RUN_JOBS_REGION=%GCP_REGION% --set-env-vars="GCP_PROJECT_ID=%GCP_PROJ_ID%" --set-env-vars="SUBSCRIPTION_ID=%GCP_PUBSUB_SUBSCRIPTION%" --set-env-vars="GCP_DATASET_ID=%BQ_DATASET_ID%" --set-env-vars="GCP_TABLE_ID=%BQ_TABLE_ID%"
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: 
	EXIT /B
)

rem List the Cloud Run Jobs by JOB URI
CALL gcloud run jobs list --uri

rem Delete any existing Scheduler Jobs
rem gcloud scheduler jobs delete SCHEDULER_JOB_NAME --location=REGION --quiet
CALL gcloud scheduler jobs delete %GCP_RUN_JOB_PUB% --location=%GCP_REGION% --quiet
CALL gcloud scheduler jobs delete %GCP_RUN_JOB_SUB% --location=%GCP_REGION% --quiet

rem Create a Schedule Job to execute a Cloud Run Job for the publisher using its URI
rem gcloud scheduler jobs create COMMAND SCHEDULER_JOB_NAME --location=SCHEDULER_REGION --schedule="SCHEDULE" --uri="https://CLOUD_RUN_REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT-ID/jobs/JOB-NAME:run" --oauth-service-account-email SERVICE_ACCOUNT_EMAIL
CALL gcloud scheduler jobs create http %GCP_RUN_JOB_PUB% --location=%GCP_REGION% --schedule="*/2 * * * *" --uri=https://%GCP_REGION%-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/%GCP_PROJ_ID%/jobs/%GCP_RUN_JOB_PUB%:run --oauth-service-account-email %GCP_SVC_ACT%
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud scheduler jobs create http %GCP_RUN_JOB_PUB% --location=%GCP_REGION% --schedule="*/2 * * * *" --uri=https://%GCP_REGION%-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/%GCP_PROJ_ID%/jobs/%GCP_RUN_JOB_PUB%:run --oauth-service-account-email %GCP_SVC_ACT%
	EXIT /B
)

rem Create a Schedule Job to execute a Cloud Run Job for the subscriber using its URI
rem gcloud scheduler jobs create COMMAND SCHEDULER_JOB_NAME --location=SCHEDULER_REGION --schedule="SCHEDULE" --uri="https://CLOUD_RUN_REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT-ID/jobs/JOB-NAME:run" --oauth-service-account-email SERVICE_ACCOUNT_EMAIL
CALL gcloud scheduler jobs create http %GCP_RUN_JOB_SUB% --location=%GCP_REGION% --schedule="*/2 * * * *" --uri=https://%GCP_REGION%-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/%GCP_PROJ_ID%/jobs/%GCP_RUN_JOB_SUB%:run --oauth-service-account-email %GCP_SVC_ACT%
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud scheduler jobs create http %GCP_RUN_JOB_SUB% --location=%GCP_REGION% --schedule="*/2 * * * *" --uri=https://%GCP_REGION%-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/%GCP_PROJ_ID%/jobs/%GCP_RUN_JOB_SUB%:run --oauth-service-account-email %GCP_SVC_ACT%
	EXIT /B
)

rem List the Cloud Run Jobs by JOB URI
echo.
echo Google Run Jobs:
CALL gcloud run jobs list
CALL gcloud run jobs list --uri

rem List Scheduler Jobs
echo.
echo Google Scheduler Jobs:
rem gcloud scheduler jobs list --location=REGION
CALL gcloud scheduler jobs list --location=%GCP_REGION%



ENDLOCAL

echo.
echo This batch file %~n0%~x0 has ended normally (no errors).  
echo You may continue with gcp_part6.bat