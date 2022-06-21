# cardano-skepsis-toolbox
A cardano-cli based toolbox written in Python. Cardano-node must be running and environment paths exported.

Toolbox for various cardano related operations.
1. Send native tokens/nfts to a number of addresses or staking addresses
2. Monitor a payment address for incoming payments and return tokens or refunds
3. Withdraw rewards from pool
4. Send ADA simple transaction
5. Send ADA and native tokens to one destination
6. Generate SPO certificates and register on blockchain
7. Rotate KES keys

Installation:
1. Install Python3: sudo apt install python3
2. Install pip for python3: sudo apt-get install build-essential libssl-dev libffi-dev python-dev / sudo apt install python3-pip
3. Optional: Install venv for python3: sudo pip3 install virtualenv 
4. Optional: python3 -m venv venv
5. Optional: source venv/bin/activate
6. pip install --upgrade pip
7. pip install -r requirements.txt

Testing:
In a terminal (Optional: with the virtual environment venv activated (Step 2 of installation)):
python -m unittest

USAGE:
To withdraw all pool rewards to a payment address:
    python3 withdraw_rewards.py --payment-addr-file <filepath>
                                --payment-skey-file <filepath>
                                --stake-addr-file <filepath>
                                --stake-skey-file <filepath>
                                --sign / --submit < Signing has to be done without internet connection, submitting with internet connection >
                                                < Also stake skey has to be removed before submitting >

To send only ADA from payment address to destination:
    python3 sendADA.py --payment-addr-file <filepath>
                       --payment-skey-file <filepath>
                       --destination <filepath or cardano address string>
                       --amount-lovelace <integer amount to send in lovelace>

To send multiple assets and ada to multiple recipients:
    Edit config.json
    Create recipient list with Objects from Class cardano_cli_helper/Recipient
    Run send_assets_to_recipients.py

To monitor an address for incoming payments so that tokens are returned (run as a service):
    Edit config.json
    Run monitor_addr_service.py

To get_delegators_stake.py (Run as a crontab job every epoch):
    Edit config.json
    Run get_delegators_stake.py

To send multiple tokens to a destination:
    python3 sendTokens.py --payment-addr-file <filepath>
                          --payment-skey-file <filepath>
                          --destination <filepath or cardano address string>
                          --amount-lovelace <integer amount to send in lovelace>
                          --token-policy-id [Space separated list of token policies]
                          --token-amount [Space separated list of amounts per token policy ID]
                          --network <mainnet or testnet-magic NNNN etc>
