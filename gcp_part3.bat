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


rem import the GCP project constants from file gcp_constants.bat
if EXIST "gcp_constants.bat" (
  for /F "tokens=*" %%I in (gcp_constants.bat) do set %%I
) ELSE (
  echo ERROR: unable to find gcp_constants.bat
  EXIT /B
)


rem ----------------------------------------------------------------------

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



rem ----------------------------------------------------------------------


echo.
echo This batch file will configure Google Pub/Sub messaging with the above settings (check them carefully).  
echo Press ENTER to continue, or CTRL-C to abort.
pause


rem Add Google Pub/Sub roles to the service account
rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:some-name@some-project.iam.gserviceaccount.com --role=roles/pubsub.publisher
Call gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/pubsub.publisher
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/pubsub.publisher
	EXIT /B
)

rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:some-name@some-project.iam.gserviceaccount.com --role=roles/pubsub.subscriber
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/pubsub.subscriber
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/pubsub.subscriber
	EXIT /B
)

rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:some-name@some-project.iam.gserviceaccount.com --role=roles/pubsub.viewer
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/pubsub.viewer
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/pubsub.viewer
	EXIT /B
)

rem View the roles for the project
CALL gcloud projects get-iam-policy %GCP_PROJ_ID%
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects get-iam-policy %GCP_PROJ_ID% 
	EXIT /B
)

rem Enable Google Pub/Sub API
CALL gcloud services enable pubsub.googleapis.com
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud services enable pubsub.googleapis.com
	EXIT /B
)

rem List the enabled API services
echo.
@echo on
CALL gcloud services list
@echo off
echo Above are the enabled APIs.  Press RETURN to continue.
pause


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

rem Create a Google Pub/Sub topic for the active/default project
rem gcloud pubsub topics create TOPIC
CALL gcloud pubsub topics create %GCP_PUBSUB_TOPIC%
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud pubsub topics create %GCP_PUBSUB_TOPIC%
	EXIT /B
)

rem Create a Pub/Sub Pull subscription attached to the topic just created with exactly-once-delivery enabled.
rem gcloud pubsub subscriptions create SUBSCRIPTION --topic TOPIC
CALL gcloud pubsub subscriptions create %GCP_PUBSUB_SUBSCRIPTION% --topic %GCP_PUBSUB_TOPIC% --enable-exactly-once-delivery
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud pubsub subscriptions create %GCP_PUBSUB_SUBSCRIPTION% --topic %GCP_PUBSUB_TOPIC% --enable-exactly-once-delivery
	EXIT /B
)

rem List topics
echo.
@echo on
CALL gcloud pubsub topics list
@echo off


rem List subscriptions
echo.
@echo on
CALL gcloud pubsub subscriptions list
@echo off





ENDLOCAL

echo.
echo This batch file %~n0%~x0 has ended normally (no errors).  
echo You may continue with gcp_part4.bat