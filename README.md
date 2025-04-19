```
termux-setup-storage
```
```
yes | pkg update && pkg upgrade
yes | pkg install python git wget
pip install psutil
mkdir ccminer && cd ccminer
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/ccminer
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/config.json
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/start.sh
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/miner_ui.py
curl -sL  https://raw.githubusercontent.com/maluuux/cc-miner/main/bashrc_extras.sh >> ~/.bashrc
chmod +x miner_ui.py
chmod +x ccminer start.sh  && python3 miner_ui.py
