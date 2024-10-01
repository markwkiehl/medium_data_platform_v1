@echo off
cls
echo %~n0%~x0   version 0.0.0
echo.

rem Created by Mechatronic Solutions LLC
rem Mark W Kiehl
rem
rem LICENSE: MIT


rem Batch files: https://tutorialreference.com/batch-scripting/batch-script-tutorial
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
rem echo GCP_PUBSUB_TOPIC: %GCP_PUBSUB_TOPIC%
rem SET GCP_PUBSUB_SUBSCRIPTION=streaming_data_packet_subscription
rem echo GCP_PUBSUB_SUBSCRIPTION: %GCP_PUBSUB_SUBSCRIPTION%


rem Docker image names
rem SET GCP_IMAGE_PUB=data-platform-pub
echo GCP_IMAGE_PUB: %GCP_IMAGE_PUB%
rem SET GCP_IMAGE_SUB=data-platform-sub
echo GCP_IMAGE_SUB: %GCP_IMAGE_SUB%

rem Google Artifacts Registry repository
rem SET GCP_REPOSITORY=repo-data-platform
echo GCP_REPOSITORY: %GCP_REPOSITORY%



rem ----------------------------------------------------------------------


echo.
echo This batch file will configure and build Docker images with the above settings (check them carefully).  
echo The default Python version of 3.12 and the script names 'gcp_data_platform_pub.py' and gcp_data_platform_sub.py'
echo are already configured in the Docker files "Dockerfile-pub.txt" and "Dockerfile-sub.txt". 
echo If you changed any of these, then you must edit the files "Dockerfile-pub.txt" and "Dockerfile-sub.txt". 
echo File "Dockerfile-pub.txt" will be copied to "Dockerfile" and a Docker image will be built from it. 
echo Later "Dockerfile-sub.txt" will be copied to "Dockerfile" and a Docker image built for it.  
echo A Google Artifact repository named %GCP_REPOSITORY% will be created (deleted first if it exists), 
echo and then the Docker images will be pushed to it. 
echo Press ENTER to continue, or CTRL-C to abort.
pause

echo.

rem Define the path to the Python virtual environment Scripts folder.
rem PATH_SCRIPT already defined previously and is the path to this batch file.
SET PATH_VENV_SCRIPTS=%PATH_SCRIPT%Scripts
echo PATH_VENV_SCRIPTS: %PATH_VENV_SCRIPTS%
IF NOT EXIST "%PATH_VENV_SCRIPTS%\." (
	echo ERROR: PATH_VENV_SCRIPTS path not found.  %PATH_VENV_SCRIPTS%
	EXIT /B
)

rem Update the requirements.txt file with the currently install Python libraries for the virtual environment. 
rem Since PIP is called from a batch file, it is necessary to modify the redirect of the standard output.
rem This redirection modification is the 1> where the 1 specifies STDOUT.  
rem Other solutions other than using pip freeze are:  pipregs or pigar    

rem delete the requirements.txt file if it exists
IF EXIST "%PATH_SCRIPT%requirements.txt" (
	CALL del requirements.txt /Q
)

rem Build the requirements.txt file
echo Rebuilding the Python package installation list requirements.txt ..
@echo on
CALL "%PATH_VENV_SCRIPTS%\pip3.exe" freeze 1> requirements.txt
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

rem Copy file "Dockerfile-pub.txt" to "Dockerfile
CALL copy /Y Dockerfile-pub.txt Dockerfile

rem Make sure a Dockerfile exists
IF NOT EXIST "%PATH_SCRIPT%Dockerfile" (
echo ERROR: File not found.  %PATH_SCRIPT%Dockerfile
EXIT /B
)

rem Build the Docker image with the name "data-platform-pub"
rem docker build -t IMAGE .
@echo on
CALL docker build -t data-platform-pub .
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: docker build -t data-platform-pub .
	EXIT /B
)

rem Tag the local Docker image "data-platform-pub"
rem docker tag SOURCE-IMAGE LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE:TAG
@echo on
CALL docker tag %GCP_IMAGE_PUB% %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/repo-data-platform/data-platform-pub
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: docker tag %GCP_IMAGE_PUB% %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/repo-data-platform/data-platform-pub
	EXIT /B
)

echo.
echo To run the Docker image "data-platform-pub" in a Docker container:
echo docker run -it -e GCP_RUN_JOBS_REGION=%GCP_REGION% -v "%appdata%//gcloud"://root/.config/gcloud %GCP_IMAGE_PUB%:latest
echo.

rem Copy file "Dockerfile-sub.txt" to "Dockerfile
@echo on
CALL copy /Y Dockerfile-sub.txt Dockerfile
@echo off

rem Make sure a Dockerfile exists
IF NOT EXIST "%PATH_SCRIPT%Dockerfile" (
echo ERROR: File not found.  %PATH_SCRIPT%Dockerfile
EXIT /B
)

rem Build the Docker image with the name "data-platform-sub"
rem docker build -t IMAGE .
@echo on
CALL docker build -t data-platform-sub .
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: docker build -t data-platform-sub .
	EXIT /B
)

rem Tag the local Docker image "data-platform-sub"
rem docker tag SOURCE-IMAGE LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE:TAG
@echo on
CALL docker tag %GCP_IMAGE_SUB% %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/repo-data-platform/data-platform-sub
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: docker tag %GCP_IMAGE_SUB% %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/repo-data-platform/data-platform-sub
	EXIT /B
)

echo.
echo To run the Docker image "data-platform-sub" in a Docker container:
echo docker run -it -e GCP_RUN_JOBS_REGION=%GCP_REGION% -v "%appdata%//gcloud"://root/.config/gcloud %GCP_IMAGE_SUB%:latest
echo.

rem --------------------------------------------------------------------------------------
rem Create a repository in Google Artifacts and push the Docker images to it

rem Enable Google Artifact Registry API 
CALL gcloud services enable artifactregistry.googleapis.com
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud services enable artifactregistry.googleapis.com
	EXIT /B
)

rem In order to manage the conflict where Docker images already exist in a repository
rem and we wish to upload a new file, the Google Artificts repository will be deleted (deletes the files).
rem Delete a repository
rem gcloud artifacts repositories delete REPOSITORY [--location=LOCATION] [--async]
echo.
echo Deleting the repository '%GCP_REPOSITORY%' and its files (if they exist).
echo Ignore any error messages.
@echo on
CALL gcloud artifacts repositories delete %GCP_REPOSITORY% --location=%GCP_REGION% --quiet
@echo off


rem Create a repository in Google Artifact Registry using the gcloud CLI (it may already exist)
rem gcloud artifacts repositories create REPOSITORY --repository-format=docker --location=LOCATION --description="A CUSTOM DESCRIPTION OF THE REPO"
echo.
@echo on
CALL gcloud artifacts repositories create %GCP_REPOSITORY% --repository-format=docker --location=%GCP_REGION% --description="data_platform pub and sub Docker images"
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo Ignore the above error if the repository already exists. 
)


rem List repositories for the location and project
rem gcloud artifacts repositories list [--project=PROJECT] [--location=LOCATION]
@echo on
CALL gcloud artifacts repositories list --project=%GCP_PROJ_ID% --location=%GCP_REGION%
@echo off

rem Show information about a Google repository created
rem gcloud artifacts repositories describe <REPOSITORY> --location=LOCATION
echo.
@echo on
CALL gcloud artifacts repositories describe %GCP_REPOSITORY% --location=%GCP_REGION%
@echo off



rem Grant the user-managed service account the role required for Google Cloud Build
rem gcloud projects add-iam-policy-binding PROJECT_ID --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/cloudbuild.builds.builder
CALL gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/cloudbuild.builds.builder
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud projects add-iam-policy-binding %GCP_PROJ_ID% --member=serviceAccount:%GCP_SVC_ACT% --role=roles/cloudbuild.builds.builder
	EXIT /B
)


rem moved "gcloud services enable artifactregistry.googleapis.com" earlier from here


rem Configure authentication to Artifact Registry for Docker
rem gcloud auth configure-docker LOCATION-docker.pkg.dev
rem NOTE: Another method that may work is:  gcloud auth configure-docker gcr.io
@echo on
CALL gcloud auth configure-docker %GCP_REGION%-docker.pkg.dev
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: gcloud auth configure-docker %GCP_REGION%-docker.pkg.dev
	EXIT /B
)

rem Update local ADC
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


rem Tag the local Docker image "data-platform-pub"
rem docker tag SOURCE-IMAGE LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE:TAG
echo.
@echo on
CALL docker tag %GCP_IMAGE_PUB% %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/repo-data-platform/data-platform-pub
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: docker tag %GCP_IMAGE_PUB% %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/repo-data-platform/data-platform-pub
	EXIT /B
)

rem List the local Docker images
echo.
@echo on
CALL docker image ls
@echo off

rem Push the tagged image named "data-platform-pub" to Artifact Registry in the repository named "repo-data-platform"
rem docker push LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE
echo.
@echo on
CALL docker push %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY%/%GCP_IMAGE_PUB%
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: docker push %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY%/%GCP_IMAGE_PUB%
	EXIT /B
)

rem Push the tagged image named "data-platform-sub" to Artifact Registry in the repository named "repo-data-platform"
rem docker push LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE
echo.
@echo on
CALL docker push %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY%/%GCP_IMAGE_SUB%
@echo off
IF %ERRORLEVEL% NEQ 0 (
	echo ERROR %ERRORLEVEL%: docker push %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY%/%GCP_IMAGE_SUB%
	EXIT /B
)

rem List all files in a repository:
rem gcloud artifacts files list --repository=REPOSITORY --location=LOCATION
rem CALL gcloud artifacts files list --repository=%GCP_REPOSITORY% --location=%GCP_REGION%

rem List all files in a repository by tags
echo.
@echo on
echo Docker images in Google Artifacts repository %GCP_REPOSITORY% %GCP_REGION% %GCP_PROJ_ID%
@echo off
rem gcloud artifacts docker images list LOCATION-docker.pkg.dev/PROJECT/REPOSITORY --include-tags
CALL gcloud artifacts docker images list %GCP_REGION%-docker.pkg.dev/%GCP_PROJ_ID%/%GCP_REPOSITORY% --include-tags


ENDLOCAL

echo.
echo This batch file %~n0%~x0 has ended normally (no errors).
echo You may continue with gcp_part5.bat
