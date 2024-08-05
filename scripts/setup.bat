@echo off
setlocal EnableDelayedExpansion

rem This script is used to help the user setup the entire project

echo "---------------------------------"
echo "  __  __          _____          "
echo " |  \/  |   /\   |  __ \         "
echo " | \  / |  /  \  | |__) |   _    "
echo " | |\/| | / /\ \ |  ___/ | | |   "
echo " | |  | |/ ____ \| |   | |_| |   "
echo " |_|  |_/_/    \_\_|    \__, |   "
echo "                         __/ |   "
echo "                        |___/    "
echo "---------------------------------"

echo Welcome to the MAPy setup script!
echo Press any key to continue...
pause >nul

rem Check if Docker is running
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo Docker is installed and running.
    echo Proceeding with Docker setup...
    rem Setup the Docker container
    docker build -t mapy .

    rem Ask the user for the port (default is 8080)
    set /p "port=Please enter the port for the Docker container (default is 8080): "
    if not defined port set port=8080

    rem Validate the port
    call :CHECK_PORT %port%
    if "!isValidPort!"=="false" (
        echo Invalid port. Please enter a port number between 1 and 65535:
        set /p "port="
        call :CHECK_PORT %port%
    )

    echo Starting MAPy container on port !port!...
    docker run -p !port!:!port! --name mapy mapy
) else (
    rem Setup a local environment
    echo It appears that Docker is not installed or the Docker daemon is not running.
    echo Would you like to setup a local environment instead? (y/n^)
    set /p "yn="
    if /i "!yn!"=="y" (
        echo Setting up local environment...
    ) else (
        echo Exiting...
        exit /b
    )

    rem Check if Python is installed
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo Python installation found. Proceeding...
    ) else (
        echo Python is not installed. Please install Python 3.10 or higher.
        echo Exiting...
        exit /b
    )

    rem Ask the user for the host (default is 127.0.0.1)
    set /p "host=Please enter the host for the local environment (default is 127.0.0.1): "
    if not defined host set host=127.0.0.1

    rem Ask the user for the port (default is 8080)
    set /p "port=Please enter the port for the local environment (default is 8080): "
    if not defined port set port=8080

    rem Validate the port
    call :CHECK_PORT %port%
    if "!isValidPort!"=="false" (
        echo Invalid port. Please enter a port number between 1 and 65535:
        set /p "port="
        call :CHECK_PORT %port%
    )

    rem Setup python virtual environment
    python -m venv .venv
    call .venv\Scripts\activate

    rem Install dependencies
    pip install -r requirements.txt

    rem Run the app with the user's configuration
    echo Starting MAPy on !host!:!port!...
    python start.py -b !host! -p !port!
)

rem Function to check if the port is valid
:CHECK_PORT
set port=%1
if not defined port set port=8080
if "%port%"=="0" (
    set "isValidPort=false"
) else (
    set "isValidPort=true"
    for /L %%i in (1,1,65535) do (
        if "!port!"=="%%i" set "isValidPort=true"
    )
)
exit /b

endlocal