# MAPy

[![Python3](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Build Status](https://github.com/dan-koller/mapy/actions/workflows/python-app.yml/badge.svg)](https://github.com/dan-koller/mapy/actions/workflows/python-app.yml)

MAPy is a small utility tool for **M**ail **A**nalysis in **Py**thon. It is designed to help you parse email data and extract useful information from it such as:

-   📧 Get an overview of basic mail data (like subject, recipient, etc.)
-   📅 Extract date and time information
-   📬 Identify the source of the mail
-   🌍 Display the path the mail tookå
-   📝 Extract the content of the mail
-   🕒 Get the delays between the different steps of the mail delivery

## Get started

Download the latest release from the [releases page](https://github.com/dan-koller/mapy/releases) and use the [setup.sh](setup.sh) (Mac & Linux) or [setup.bat](setup.bat) (Windows) script to set up the app via Docker or locally. For more detailed instructions, see the [installation guide](docs/INSTALLATION.md).

If you are already familiar with Git, you can use the commands below to clone the repository and run the setup script.

### Quickstart

To get the app up and running on Mac or Linux, run:

```bash
git clone https://github.com/dan-koller/mapy.git && cd mapy && chmod +x setup.sh && ./setup.sh
```

On Windows, open a command prompt (cmd) and run:

```cmd
git clone https://github.com/dan-koller/mapy.git && cd mapy && setup.bat
```

Follow the instructions in the terminal to start the app. By default, it will be available at [http://localhost:8080](http://localhost:8080). If you want to use SSL, see the [Securing the app with SSL](docs/INSTALLATION.md#securing-the-app-with-ssl) section in the installation guide.

### Usage

It's simple! Just copy the email data you want to analyze and paste it into the input field and click the "Analyze" button. The app will then display the results in a structured way.

To learn more about the app, how to use it and how to obtain the email data you want to analyze, see the [user guide](docs/USER_GUIDE.md).
