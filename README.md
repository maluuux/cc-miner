```
termux-setup-storage
```
```
pkg update && pkg upgrade -y
pkg install git wget python -y
mkdir ccminer && cd ccminer
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/ccminer
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/config.json
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/start.sh
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/miner_ui.py
curl -sL  https://raw.githubusercontent.com/maluuux/cc-miner/main/bashrc_extras.sh >> ~/.bashrc
chmod +x miner_ui.py
chmod +x ccminer start.sh  && python3 miner_ui.py
