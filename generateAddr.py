import cardano_cli_helper as cli
import argparse
from os.path import exists


def main(fundingAddrFile, fundingSkeyFile, network='mainnet'):
    if not exists(fundingAddrFile):
        print('ERROR: Funding address file does not exist.')
        return 0
    if not exists(fundingSkeyFile):
        print('ERROR: Funding skey file does not exist.')
        return 0

    cli.generatePaymentKeyPair()
    cli.generatePaymentAddress(network)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--funding-addr-file',
                    default = '/home/christos/IOHK/repos/cardano-node/running_block_producer/mambaQAPool/payment.addr',
                    dest='funding_addr_file',
                    help='Provide location of funding address file.',
                    type=str,
                    )
    parser.add_argument('-K', '--funding-skey-file',
                    default = '/home/christos/IOHK/repos/cardano-node/running_block_producer/mambaQAPool/payment.skey',
                    dest='funding_skey_file',
                    help='Provide location of funding skey file.',
                    type=str,
                    )
    parser.add_argument('-N', '--network',
                    default='testnet-magic 9',
                    dest='network',
                    help='Provide cardano network.',
                    type=str
                    )
    args = parser.parse_args()

    main(args.funding_addr_file,
         args.funding_skey_file,
         args.network)
