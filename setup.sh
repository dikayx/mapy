#!/bin/zsh

# This script is used to help the user setup the entire project

banner=$(cat << "EOF"
--------------------------------
  __  __          _____       
 |  \/  |   /\   |  __ \      
 | \  / |  /  \  | |__) |   _ 
 | |\/| | / /\ \ |  ___/ | | |
 | |  | |/ ____ \| |   | |_| |
 |_|  |_/_/    \_\_|    \__, |
                         __/ |
                        |___/ 
--------------------------------
EOF
)

echo "$banner"
echo "Welcome to the MAPy setup script!"
echo "Press any key to continue..."
read -n 1 -s

# Function to check if the port is valid
is_valid_port() {
    local port=$1
    if [[ $port =~ ^[0-9]+$ ]] && [ $port -ge 1 ] && [ $port -le 65535 ]; then
        return 0
    else
        return 1
    fi
}

# Check if Docker is running
DOCKER_INSTALLED=$(docker info > /dev/null 2>&1)

if [ -n "$DOCKER_INSTALLED" ]; then
    echo "Docker is installed and running."
    echo "Proceeding with Docker setup..."
    # Setup the Docker container
    docker build -t mapy .

    # Ask the user for the port (default is 8080)
    echo "Please enter the port for the Docker container (default is 8080):"
    read -p "" port
    port=${port:-8080}

    # Validate the port
    while ! is_valid_port $port; do
        echo "Invalid port. Please enter a port number between 1 and 65535:"
        read -p "" port
        port=${port:-8080}
    done

    echo "Starting MAPy container on port $port..."
    docker run -p $port:$port --name mapy mapy
else
    # Setup a local environment
    echo "It appears that Docker is not installed or the Docker daemon is not running."
    echo "Would you like to setup a local environment instead? (y/n)"
    while true; do
        read -p "" yn
        case $yn in
            [Yy]* ) echo "Setting up local environment..."; break;;
            [Nn]* ) echo "Exiting..."; exit;;
            * ) echo "Please answer 'y' or 'n'.";;
        esac
    done

    # Check if Python 3 is installed
    PYTHON_INSTALLED=$(python3 --version > /dev/null 2>&1)
    if [ -n "$PYTHON_INSTALLED" ]; then
        echo "Python 3 installation found. Proceeding..."
    else
        echo "Python 3 is not installed. Please install Python 3.10 or higher."
        echo "Exiting..."
        exit
    fi

    # Ask the user for the host (default is 127.0.0.1)
    echo "Please enter the host for the local environment (default is 127.0.0.1):"
    read -p "" host
    host=${host:-127.0.0.1}

    # Ask the user for the port (default is 8080)
    echo "Please enter the port for the local environment (default is 8080):"
    read -p "" port
    port=${port:-8080}

    # Validate the port
    while ! is_valid_port $port; do
        echo "Invalid port. Please enter a port number between 1 and 65535:"
        read -p "" port
        port=${port:-8080}
    done

    # Setup python virtual environment
    python3 -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip3 install -r requirements.txt

    # Run the app with the user's configuration
    echo "Starting MAPy on $host:$port..."
    .venv/bin/python start.py -b $host -p $port
fi