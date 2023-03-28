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

Installation with python virtual environment:
1. Install Python3: sudo apt install python3
2. Install pip for python3: sudo apt-get install build-essential libssl-dev libffi-dev python-dev / sudo apt install python3-pip
3. Optional: Install venv for python3: sudo pip3 install virtualenv
4. Optional: python3 -m venv venv
5. Optional: source venv/bin/activate
6. pip install --upgrade pip
7. pip install -r requirements.txt

Installation with nix environment:
1. nix develop

Testing:
In a terminal (Optional: with the virtual environment venv activated (Step 2 of installation)):
python -m unittest

USAGE:
To send multiple tokens to a destination:
```shell
    python3 sendTokens.py --payment-addr <filepath or cardano address string>
                          --payment-skey-file <filepath>
                          --destination <filepath or cardano address string>
                          --amount-lovelace <integer amount to send in lovelace>
                          --token-policy-id [Space separated list of token policies to send]
                          --token-amount [Space separated list of amounts per token policy ID]
                          --network <mainnet or testnet-magic NNNN etc>
                          --era Current era (e.g. alonzo-era, babbage-era etc)
```
    The script will automatically calculate the (min) amount of ADA for the return utxo of any native tokens.
    *If you want to send the min amount of ADA to a recipient with native token(s), set amount-lovelace=0.*

To clean an account of all (or most) native tokens:
```shell
    python3 cleanAddress.py --payment-addr <filepath or cardano address string>
                            --payment-skey-file <filepath>
                            --destination <filepath or cardano address string>
                            --keep-token-policy-id [Space separated list of token policies to keep]
                            --network <mainnet or testnet-magic NNNN etc>
                            --era Current era (e.g. alonzo-era, babbage-era etc)
```
    The script will automatically calculate the min amount of ADA to send with the tokens.

To withdraw all pool rewards to a payment address:
```shell
    python3 withdraw_rewards.py --payment-addr-file <filepath>
                                --payment-skey-file <filepath>
                                --stake-addr-file <filepath>
                                --stake-skey-file <filepath>
                                --sign / --submit < Signing has to be done without internet connection, submitting with internet connection >
                                                < Also stake skey has to be removed before submitting >
```

To send only ADA from payment address to destination: (Legacy, use sendTokens.py)
```shell
    python3 sendADA.py --payment-addr-file <filepath>
                       --payment-skey-file <filepath>
                       --destination <filepath or cardano address string>
                       --amount-lovelace <integer amount to send in lovelace>
```

To send multiple assets and ada to multiple recipients:
    Edit config.json
    Create recipient list with Objects from Class cardano_cli_helper/Recipient
    Run send_assets_to_recipients.py

To monitor an address for incoming payments so that tokens are returned (run as a service):
    If you want to use Blockfrost to find the sender's address please provide a valid API key.
    Otherwise only use simple transactions, 1 TxIn, 1 TxOut (+ change) where the sender's address
    is assumed to be the next TxIx from the one received.
    The variable MODE can be set to "marketplace" or "delegators". In the former mode the tokens are dispensed
    based on a ADA/token ratio minus fees. In the later mode the tokens are dispensed based on the amount of
    stake per epoch staked on your pool by the delegator, who has to send ADA from an address that is controlled
    by the stake key associated with your pool.
    Edit config.json
    Run monitor_addr_service.py

To get_delegators_stake.py (Run as a crontab job every epoch):
    Edit config.json
    Run get_delegators_stake.py



## Examples:

### Register a new SPO:

In an empty folder run:

```shell
python3 /path/to/registerSPO.py \
  --funding-addr-file /path/to/payment.addr \
  --funding-skey-file /path/to/payment.skey \
  --network 'testnet-magic 7' \
  --name "MY-SPO-NAME" --ticker 'AAAA'
```