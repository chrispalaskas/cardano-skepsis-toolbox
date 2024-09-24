import cardano_cli_helper as cli
import argparse
from os.path import exists


def main(network, era, payment_addr_file, payment_skey_file, destination_addr, lovelace_amount,
         token_amount, token_policy_id, token_policy_script, token_policy_skey):
    if not exists(payment_addr_file):
        print('ERROR: Payment address file does not exist.')
        return 0
    else:
        with open(payment_addr_file, 'r') as file:
            payment_addr = file.read().strip()
    if not exists(payment_skey_file):
        print('ERROR: Payment skey file does not exist.')
        return 0
    if not exists(token_policy_skey):
        print('ERROR: Token skey file does not exist.')
        return 0        
    if exists(destination_addr): # If it doesn't exist assume it's a valid address
        with open(destination_addr, 'r') as file:
            destination_addr = file.read().strip()
    lovelace, utxos = cli.getLovelaceBalance(payment_addr, network)
    print(lovelace)
    print(utxos)
    txIn = utxos[0]
    change_address = payment_addr
    cli.buildMintTokensTx(network, era, txIn, change_address, destination_addr, lovelace_amount, 
                          token_amount, token_policy_id, token_policy_script)
    signingKeys = [payment_skey_file,
                   token_policy_skey]
    cli.signTx(signingKeys,network=network)
    cli.submitSignedTx(network=network)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--payment-addr-file',
                    default='/home/christos/IOHK/repos/mamba-world/SPOs/spo1/payment.addr',
                    dest='payment_addr_file',
                    help='Provide location of payment address file.',
                    type=str
                    )
    parser.add_argument('-K', '--payment-skey-file',
                    default='/home/christos/IOHK/repos/mamba-world/SPOs/spo1/payment.skey',
                    dest='payment_skey_file',
                    help='Provide location of payment skey file.',
                    type=str
                    )
    parser.add_argument('-D', '--destination',
                    default='/home/christos/IOHK/repos/mamba-world/SPOs/spo2/payment.addr',
                    dest='destination',
                    help='Provide location destination address file or string.',
                    type=str
                    )
    parser.add_argument('-L', '--amount-lovelace',
                    default=1444443,
                    dest='lovelace_amount',
                    help='Provide amount to send in lovelace.',
                    type=int
                    )
    parser.add_argument('-N', '--network',
                    default='testnet-magic 9',
                    dest='network',
                    help='Provide cardano network.',
                    type=str
                    )
    parser.add_argument('-E', '--era',
                    default='conway-era',
                    dest='era',
                    help='Provide current era.',
                    type=str
                    )
    parser.add_argument('-T', '--token-amount',
                    default=100000000000,
                    dest='token_amount',
                    help='Provide number of tokens to mint.',
                    type=int
                    )
    parser.add_argument('-P', '--token-policy-id',
                    default='6f1e7de82f60f7bb4edde75b8b1cefb12a12d88e20e318947c1c130b.4655454c',
                    dest='token_policy_id',
                    help='Provide policy ID of token to mint.',
                    type=str
                    )
    parser.add_argument('-S', '--token-script-file',
                    default='/opt/cardano/cnodehome/priv/asset/FuelToken/policy.script',
                    dest='token_policy_script',
                    help='Provide path to token policy script.',
                    type=str
                    )
    parser.add_argument('-TS', '--token-skey-file',
                    default='/opt/cardano/cnodehome/priv/asset/FuelToken/policy.skey',
                    dest='token_policy_skey',
                    help='Provide path to token policy skey.',
                    type=str
                    )                        

    args = parser.parse_args()

    main(args.network,
         args.era,
         args.payment_addr_file,
         args.payment_skey_file,
         args.destination,
         args.lovelace_amount,         
         args.token_amount,
         args.token_policy_id,
         args.token_policy_script,
         args.token_policy_skey)
