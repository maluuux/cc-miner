```
termux-setup-storage
```
```
pkg install termux-api -y
termux-wake-lock
pkg update && pkg upgrade -y
pkg install python git wget -y
pip install colorama requests
mkdir ccminer && cd ccminer
wget https://raw.githubusercontent.com/maluuux/termux-miner/main/ccminer
wget https://raw.githubusercontent.com/maluuux/termux-miner/main/config.json
wget https://raw.githubusercontent.com/maluuux/termux-miner/main/start.sh
wget https://raw.githubusercontent.com/maluuux/termux-miner/main/miner_ui.py
curl -sL  https://raw.githubusercontent.com/maluuux/termux-miner/main/bashrc_extras.sh >> ~/.bashrc
chmod +x miner_ui.py
chmod +x ccminer start.sh  && python3 miner_ui.py
