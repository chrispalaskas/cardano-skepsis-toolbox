import cardano_cli_helper as cli
import argparse
from os.path import exists


def main(paymentAddrFile, paymentSkeyFile, recipientAddr, lovelace_amount, network='mainnet'):
    if not exists(paymentAddrFile):
        print('ERROR: Payment address file does not exist.')
        return 0
    else:
        with open(paymentAddrFile, 'r') as file:
            paymentAddr = file.read().strip()
    if not exists(paymentSkeyFile):
        print('ERROR: Payment skey file does not exist.')
        return 0
    if exists(recipientAddr):
        with open(recipientAddr, 'r') as file:
            recipientAddr = file.read().strip()

    cli.getProtocolJson(network)
    lovelace, utxos = cli.getLovelaceBalance(paymentAddr, network)
    ttlSlot = cli.getCurrentSlot(network) + 1000
    cli.getDraftTXSimple(utxos, paymentAddr, recipientAddr, ttlSlot)
    minFee = cli.getMinFee(len(utxos),1, network)
    lovelace_return = lovelace - minFee - lovelace_amount
    cli.getRawTxSimple(utxos,paymentAddr,recipientAddr, lovelace_amount, lovelace_return, ttlSlot, minFee)
    cli.signTx(paymentSkeyFile)
    cli.submitSignedTx(network=network)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--payment-addr-file',
                    default='/home/christos/IOHK/repos/cardano-node/running_block_producer/mambaQAPool/payment.addr',
                    dest='payment_addr_file',
                    help='Provide location of payment address file.',
                    type=str
                    )
    parser.add_argument('-K', '--payment-skey-file',
                    default='/home/christos/IOHK/repos/cardano-node/running_block_producer/mambaQAPool/payment.skey',
                    dest='payment_skey_file',
                    help='Provide location of payment skey file.',
                    type=str
                    )
    parser.add_argument('-D', '--destination',
                    default='/home/christos/IOHK/repos/cardano-node/running_block_producer/mambaQAPool/gergely.addr',
                    dest='destination',
                    help='Provide location destination address file or string.',
                    type=str
                    )
    parser.add_argument('-L', '--amount-lovelace',
                    default=499990000000,
                    dest='amount',
                    help='Provide amount to send in lovelace.',
                    type=int
                    )
    parser.add_argument('-N', '--network',
                    default='testnet-magic 9',
                    dest='network',
                    help='Provide cardano network.',
                    type=str
                    )

    args = parser.parse_args()

    main(args.payment_addr_file,
         args.payment_skey_file,
         args.destination,
         args.amount,
         args.network)