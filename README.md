```
termux-setup-storage
```
```
yes | pkg update && pkg upgrade
yes | pkg install python git make cmake
yes | pkg install wget
pip install psutil colorama
mkdir ccminer && cd ccminer
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/ccminer
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/config.json
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/start.sh
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/miner_ui.py
curl -sL  https://raw.githubusercontent.com/maluuux/cc-miner/main/bashrc_extras.sh >> ~/.bashrc
chmod +x miner_ui.py
chmod +x ccminer start.sh  && python3 miner_ui.py

pkg update && pkg upgrade
pkg install git make cmake libjansson openssl
