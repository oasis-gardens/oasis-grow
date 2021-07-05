#!/bin/sh -e

echo "This setup is built for the Raspi OS release 2021-05-07-raspios-buster-armhf-lite."

echo "Adding OS packages..."
sudo apt-get update
sudo apt install -y wget software-properties-common build-essential libnss3-dev zlib1g-dev libgdbm-dev libncurses5-dev libssl-dev libffi-dev libreadline-dev libsqlite3-dev libbz2-dev
sudo apt-get install -y libopenjp2-7
sudo apt-get install -y libtiff5
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y libjpeg-dev zlib1g-dev

echo "Building Python Environment (3.9.2)..."
wget https://www.python.org/ftp/python/3.9.2/Python-3.9.2.tgz
tar xvf Python-3.9.2.tgz
cd Python-3.9.2/
./configure --enable-optimizations
sudo make altinstall
python3.9 -V

echo "Pointing all python3 to python3.9..."
alias python3=python3.9
alias pip3=pip3.9
echo "alias python3=python3.9" | sudo tee -a /home/pi/.bashrc
source /home/pi/.bashrc
echo "alias pip3=pip3.9" | sudo tee -a /home/pi/.bashrc
source /home/pi/.bashrc

echo "Configuring PATH variable..."
echo "export PATH=/home/pi/.local/bin:$PATH/" | sudo tee -a /home/pi/.bashrc
source /home/pi/.bashrc

echo "Installing modules..."
cd ..
python3.9 -m pip install -r /home/pi/oasis-grow/requirements.txt


