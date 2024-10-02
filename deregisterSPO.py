import cardano_cli_helper as cli
import argparse
from os.path import exists
import os


def main(paymentAddrFile, paymentSkeyFile, poolName, retire_epoch,
         network, era):
    if not exists(poolName):
        print(f"Please place all keys in a folder named {poolName}")
        return
    os.chdir(poolName)
    cli.createDeregistrationCert(retire_epoch, era)

    with open(paymentAddrFile) as addr_file:
        paymentAddr = addr_file.read().strip()
        print(paymentAddr)
    # If you chose to select UTxOs with other native tokens,
    # and not only ADA, you should increase the min_utxo_threshold
    lovelace, utxos = cli.getLovelaceBalance(
        paymentAddr, network, onlyAda=True
        )
    min_utxo_threshold = 1000000
    ttlSlot = cli.queryTip('slot', network) + 1000
    cli.buildCertificateFileListTx(
        ['pool-deregistration.cert'], paymentAddr, utxos, ttlSlot,
        amount=min_utxo_threshold, network=network, era=era
        )
    cli.signTx([paymentSkeyFile, 'cold.skey'], network=network)
    cli.submitSignedTx(network=network)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-A', '--payment-addr-file',
        dest='payment_addr_file',
        help='Provide location of the payment address file.',
        type=str,
        default='/home/christos/IOHK/tools/test_automation_secrets/cardano_keys/Local/local_payment.addr'
        )
    parser.add_argument(
        '-K', '--payment-skey-file',
        dest='payment_skey_file',
        help='Provide location of the payment skey file.',
        type=str,
        default='/home/christos/IOHK/tools/test_automation_secrets/cardano_keys/Local/local_payment.skey'
        )
    parser.add_argument(
        '--pool-name',
        dest='pool_name',
        help='Pool name.',
        type=str,
        default='PC_PreviewTest5'
        )
    parser.add_argument(
        '--ticker',
        dest='ticker',
        help='Pool ticker. Should be between 3 and 5 uppercase \
            characters or numbers.',
        type=str,
        default='PCPT4'
        )
    parser.add_argument(
        '--epoch-to-retire',
        dest='retire_epoch',
        help='Epoch number when pool should retire. Should be a future value.',
        type=int,
        default=710
        )
    parser.add_argument(
        '-N', '--network',
        default='testnet-magic 2',
        dest='network',
        help='Provide cardano network.',
        type=str
        )
    parser.add_argument(
        '-E', '--era',
        default='conway',
        dest='era',
        help='Provide cardano era.',
        type=str
        )
    args = parser.parse_args()

    main(args.payment_addr_file,
         args.payment_skey_file,
         args.pool_name,
         args.retire_epoch,
         args.network,
         args.era)
