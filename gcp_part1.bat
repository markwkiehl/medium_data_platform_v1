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




rem Define below the Python version GCP should use.  Recommend Python v3.12
rem py --list-paths will show what Python versions are installed.
SET GCP_PYTHON_VERSION=3.12

rem CLOUDSDK_PYTHON is used by Google Cloud CLI & SDK
rem Using %GCP_PYTHON_VERSION%, define a path to python.exe for that version and assign to CLOUDSDK_PYTHON.
rem py --list-paths will show what Python versions are installed.
rem Path example: C:\Users\[username]\AppData\Local\Programs\Python\Python312\python.exe
SET CLOUDSDK_PYTHON=%USERPROFILE%\AppData\Local\Programs\Python\Python%GCP_PYTHON_VERSION:.=%\python.exe
IF NOT EXIST "%CLOUDSDK_PYTHON%" (
echo ERROR: CLOUDSDK_PYTHON path not found.  %CLOUDSDK_PYTHON%
echo Is Python version %GCP_PYTHON_VERSION% installed?
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
echo GCP_PYTHON_VERSION: %GCP_PYTHON_VERSION%
echo CLOUDSDK_PYTHON: %CLOUDSDK_PYTHON%


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
echo The values for GCP_PYTHON_VERSION, GCP_USER, GCP_BILLING_ACCOUNT, and CLOUDSDK_PYTHON must be valid.
echo The Python version referenced by GCP_PYTHON_VERSION has been verified to already exist and the  
echo variable CLOUDSDK_PYTHON will be permanently configured to reference that Python installation location. 
echo The other local variable assignments shown will be used later by gcp_part2.bat .. gcp_part6.bat 
echo as the names assigned to subsequent project specific Google service configurations.  
echo Press ENTER to continue, or CTRL-C to abort so you can edit the file gcp_constants.bat.
pause

rem ----------------------------------------------------------------------

rem Finalize and make permanent the environment variable CLOUDSDK_PYTHON for the user. 
@echo on
CALL setx CLOUDSDK_PYTHON "%CLOUDSDK_PYTHON%"
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%:
	EXIT /B
)

echo.
echo A Python virtual environment will be created for this current working folder:
echo  %PATH_SCRIPT%
echo This folder should contain the files downloaded from GitHub.
echo.
echo Press ENTER to continue, or CTRL-C to abort so you can edit this file '%~n0%~x0'.
pause

rem cd /D %USERPROFILE%\documents

rem echo "%cd:~2%"


rem C:\Users\Mark Kiehl\AppData\Local\Programs\Python\Python312\python.exe
rem %GCP_PYTHON_VERSION%

rem Make sure PIP is installed / upgraded to the latest for Python v3.12
@echo on
CALL py -%GCP_PYTHON_VERSION% -m pip install --upgrade pip
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%:
	EXIT /B
)

rem Make sure the requirements.txt file exists.
IF NOT EXIST "%PATH_SCRIPT%requirements.txt" (
	echo ERROR: File not found.  %PATH_SCRIPT%requirements.txt
	EXIT /B
)

rem get the current folder name (only)
rem for %%* in (.) do SET THIS_FOLDER=%%~n*
for %%a in ("%cd%") do set "THIS_FOLDER=%%~nxa"

rem Change the working directory to the parent
@echo on
CALL cd ..
@echo off

rem Create a virtual envrionment in the currrent folder
echo Creating a Python virtual environment in folder '%THIS_FOLDER%'..
@echo on
CALL py -3.12 -m venv %THIS_FOLDER%
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%:
	EXIT /B
)

rem Change back to the original script path (venv folder).
@echo on
CALL cd /D %PATH_SCRIPT%
@echo off

rem Activate the virtual environment
echo Activating the Python virtual environment..
@echo on
CALL scripts\activate
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%:
	EXIT /B
)
CALL py -V

rem Check if PIP needs to be upgraded
@echo on
CALL py -m pip install --upgrade pip
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%:
	EXIT /B
)

rem Show the currently installed Python packages
echo Installed Python packages before installation from requirements.txt:
@echo on
CALL py -m pip list
@echo off
echo.

rem Install Python packages as specified in requirements.txt
@echo on
CALL py -m pip install -r requirements.txt
@echo off


echo Installed Python packages after installation from requirements.txt:
@echo on
CALL py -m pip list
@echo off
echo.

rem Deactivate the virtual environment
echo Deactivating the Python virtual environment..
@echo on
CALL scripts\deactivate
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%:
	EXIT /B
)


ENDLOCAL


echo.
echo This batch file %~n0%~x0 has ended normally (no errors).  
echo You may continue with gcp_part2.bat
EXIT /B


