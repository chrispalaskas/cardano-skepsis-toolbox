# cardano-skepsis-toolbox
A cardano-cli based toolbox written in Python

Toolbox for various cardano related operations.
1. Send native tokens/nfts to a number of addresses or staking addresses
2. Monitor a payment address for incoming payments and return tokens or refunds

Installation:
1. Install Python3: sudo apt install python3
2. Install pip for python3: sudo apt-get install build-essential libssl-dev libffi-dev python-dev / sudo apt install python3-pip
3. Optional: Install venv for python3: sudo pip3 install virtualenv 
4. Optional: python3 -m venv venv
5. Optional: source venv/bin/activate
6. pip install --upgrade pip
7. pip install -r requirements.txt
8. Edit config.json
9. run with <<python3 FILE.py>>

Testing:
In a terminal (Optional: with the virtual environment venv activated (Step 2 of installation)):
python -m unittest
