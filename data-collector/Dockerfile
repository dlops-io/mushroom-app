# The Dockerfile is simply a text file that is used to build the Docker image

# Use the official Debian-hosted Python image
FROM python:3.7-slim-buster


# the ENV instruction sets the environment variable for the Docker container when it starts up
# source: https://dockerlabs.collabnix.com/beginners/dockerfile/Lab_%239:ENV_instruction.html

# Prevent apt from showing prompts
# don't want any question/dialog asked during the 'apt-get install'
# source: https://serverfault.com/questions/618994/when-building-from-dockerfile-debian-ubuntu-package-install-debconf-noninteract
ENV DEBIAN_FRONTEND=noninteractive

# this appears to be setting the Python environment shell to be Bash
# once again, a shell just allows for running programs, giving them input, and inspecting output in a semi-structured way
# the shell is the interface that allows users to communicate with the kernel (the kernel is lowest level of the OS, which manages communication between hardware and sofware, and it manages the system's resources such as managing the CPU, memory, and peripheral devices)
# source: https://pediaa.com/difference-between-kernel-and-shell/; https://www.redhat.com/en/topics/linux/what-is-linux; MIT Missing Semester; https://www.linux.com/what-is-linux/
ENV PYENV_SHELL=/bin/bash

# the RUN command instructs the Docker daemon to run the given commands as it's creating the image; a Dockerfile can have multiple RUN commands, where each one creates a new "layer" in the image
# when building new Docker images, a previous image can be removed or replaced with a different one, which will speed up the build process
# this apt-get installs, updgrades, or uninstalls software packages; apt stands for Advanced Packaging Tool since it's a program that enables you to install, update and remove software, including taking care of dependencies. It also enables you to search for programs of interest, as well as performing other functions.
# GeckoDriver is the link between Selenium tests and the Firefox browser
# at the end here, we're removing excess files, upgrading pip, installing pipenv, and making a directory called app
# source: Pavlos lecture 13 on Docker from AC 207 in the fall; https://www.toolsqa.com/selenium-webdriver/selenium-geckodriver/; https://www.techradar.com/uk/how-to/computing/everything-you-need-to-know-about-linux-commands-1321955/2
RUN apt-get update && apt-get install -y \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
    curl unzip wget \
    xvfb && \
    GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    mkdir -p /app

# defines the working directory for the rest of the instructions in the Dockerfile; this adds metadata to the image config
# in this case, we're creating the app directory in the Docker container and will be performing subsequent commands (as seen below) from that directory
# source: https://dockerlabs.collabnix.com/beginners/dockerfile/WORKDIR_instruction.html
WORKDIR /app

# Install python packages
# the 'ADD' command is copying files from the download-images/ folder on your PC to the app/ folder on the Docker container; in this case, we're copying Pipfile and Pipfile.lock
# source: https://dockerlabs.collabnix.com/beginners/dockerfile/Lab-2-Create-an-image-with-ADD-instruction.html
ADD Pipfile Pipfile.lock /app/

# problems that pipenv solves: not having to worry about dependencies or sub-dependencies of packages (either for dependency resolution or deterministic builds); 
# you no longer have to force exact versions you don’t truly need to ensure your development and production environments are the same. You also don’t need to stay on top of updating sub-dependencies you “don’t care about.”
# pipenv introduces two files: the Pipfile (which is meant to replace requirements.txt) and the Pipfile.lock (which enables deterministic builds, meaning that the same environment will always be produced)
# source https://realpython.com/pipenv-guide/#problems-that-pipenv-solves
RUN pipenv sync

# Add source code
# you're adding the current directory on your PC to the app/ folder in the Docker container
ADD . /app

# Entry point
# the ENTRYPOINT command makes the container run as an executable
# the way this entrypoint is configured is in executable form: "ENTRYPOINT ["executable","param1","param2"]"
# what's actually happening here is we're running the Bash shell, and that will execute this docker-entrypoint.sh script
ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]
