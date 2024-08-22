# Installation

MAPy is a simple web app that allows you to parse email data and extract useful information from it. You can either run the app directly on your machine or use Docker to run it in a container.

This installation guide will show you how to set up the app locally or using Docker. There are setup scripts available for Mac & Linux [setup.sh](../setup.sh) and Windows [setup.bat](../setup.bat) that will guide you through the installation process. You can find them in the root directory of the repository.

However, if you want to set up the app manually, follow the instructions below.

## Local

MAPy requires Python 3.10 or higher to run locally.

1. Clone the repository

    ```bash
    git clone https://github.com/dikayx/mapy
    ```

2. Create a new virtual environment\* & activate it

    ```bash
    python3 -m venv .venv && source .venv/bin/activate
    ```

    > On Windows, open a command prompt and run `.venv\Scripts\activate.bat`

3. Install the required Python packages\*

    ```bash
    pip3 install -r requirements.txt
    ```

4. Run the app

    ```bash
    .venv/bin/python start.py
    ```

    - To run the app in debug mode, run `python3 start.py -d`
    - To change the port or set the host, use the `-p` and `-b` flags respectively (e.g. `python3 start.py -b 0.0.0.0 -p 8080`)
    - For more options, run `python3 start.py --help` or see the [Command line options](#command-line-options) section below

_\*) You might need to use python and pip instead of python3 and pip3 depending on your system._

> **Note**: By default, the app will be available at [http://localhost:8080](http://localhost:8080) and not secured with SSL. If you want to use SSL, see the [Securing the app with SSL](#securing-the-app-with-ssl) section below.

### Command line options

| Flag                  | Options                       | Description                                                                 |
| --------------------- | ----------------------------- | --------------------------------------------------------------------------- |
| **-h** or **--help**  | none                          | **Optional.** Show the help message                                         |
| **-d** or **debug**   | none                          | **Optional.** Run the app in debug mode                                     |
| **-p** or **port**    | Port like `8080`              | **Optional.** Set the port for the app                                      |
| **-b** or **bind**    | IP like `127.0.0.1`           | **Optional.** Set the host for the app                                      |
| **-a** or **--adhoc** | none                          | **Optional.** Use SSL with a self-signed certificate (only for development) |
| **-c** or **--cert**  | Path like `/path/to/cert.pem` | **Optional.** Path to the SSL certificate file (needs to be used with `-k`) |
| **-k** or **--key**   | Path like `/path/to/key.pem`  | **Optional.** Path to the SSL key file (needs to be used with `-c`)         |

### Securing the app with SSL

For quick & dirty tests (such as in a development environment), you can use the `-a` flag to enable SSL with a self-signed certificate. However, for production, you should use a valid SSL certificate.

1. Generate a self-signed certificate using openssl

    ```bash
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
    ```

2. Run the app with the `-c` and `-k` flags to specify the paths to the certificate and key files

    ```bash
    .venv/bin/python start.py -c /path/to/cert.pem -k /path/to/key.pem
    ```

> **Note**: The app will be available at [https://localhost:8080](https://localhost:8080) after you start it with SSL enabled. However, you might need to accept the self-signed certificate in your browser to access the app. For production, use a valid SSL certificate.

To learn more, take a look at [this article](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https) by Miguel Grinberg on how to run a Flask app over HTTPS.

## Docker

You can run the app using Docker and the `Dockerfile` provided in the repository.

1. Build the Docker image

    ```bash
    docker build -t mapy .
    ```

2. Run the Docker container

    ```bash
    docker run -p 8080:8080 --name mapy mapy
    ```

You can also use the `docker-compose.yml` file to run the app. Just run `docker-compose up` after you built the image and the app will be available on `http://localhost:8080`.

1. Clone the repository

    ```bash
    git clone https://github.com/dikayx/mapy
    cd mapy
    ```

2. Run the app using Docker Compose

    ```bash
    docker-compose up
    ```

3. Access the app on `http://localhost:8080`

    > **Note**: By default, the app will not be secured with SSL. If you want to use SSL, see the [Securing the app with SSL in Docker](#securing-the-app-with-ssl-in-docker) section below.

4. Stop the app using `Ctrl+C` and run `docker-compose down` to remove the containers

### Command line options

Same as the local installation. See the [Command line options](#command-line-options) section above.

### Securing the app with SSL in Docker

To use SSL with a self-signed certificate in Docker, you need to mount the certificate and key files into the container. Follow the steps in the [Securing the app with SSL](#securing-the-app-with-ssl) section above to generate the certificate and key files.

To secure the app with SSL in Docker, you need to mount the certificate and key files into the container. First, create a new directory and copy the certificate and key files into it. Then, run the Docker container with the following command:

```bash
docker run -p 8080:8080 -v /path/to/cert.pem:/app/cert.pem -v /path/to/key.pem:/app/key.pem --name mapy mapy -c /app/cert.pem -k /app/key.pem
```
