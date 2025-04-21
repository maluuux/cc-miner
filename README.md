```
termux-setup-storage
```
```
yes | pkg update -y
yes | pkg upgrade -y
yes | pkg install libjansson wget nano -y
yes | pkg install python -y
yes | pkg install python make clang libffi openssl libjpeg-turbo -y
pip install requests
pip install --upgrade pip wheel
pip install psutil --no-binary psutil
pkg install nano
mkdir ccminer && cd ccminer
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/ccminer
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/config.json
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/start.sh
wget https://raw.githubusercontent.com/maluuux/cc-miner/main/miner_ui.py
curl -sL  https://raw.githubusercontent.com/maluuux/cc-miner/main/bashrc_extras.sh >> ~/.bashrc
chmod +x miner_ui.py
chmod +x ccminer start.sh  && python3 miner_ui.py
