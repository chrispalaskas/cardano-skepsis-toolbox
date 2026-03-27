import cardano_cli_helper as cli
import argparse
from os.path import exists
import sendTokens


def generateAndFund(fundingAddrFile, fundingSkeyFile, network, name='payment'):
    if not exists(fundingAddrFile):
        print('ERROR: Funding address file does not exist.')
        return 0
    if not exists(fundingSkeyFile):
        print('ERROR: Funding skey file does not exist.')
        return 0

    generateAccount(network, name)
    sendTokens.main(
        fundingAddrFile,
        fundingSkeyFile,
        f'{name}.addr',
        100*pow(10, 6),
        [],
        [],
        network=network)


def generateAccount(network, name='payment'):
    cli.generatePaymentKeyPair(name)
    cli.generatePaymentAddress(network, name)


def main(withFunding, lovelace_amount, fundingAddrFile,
         fundingSkeyFile, network='mainnet', name='payment'):
    if withFunding:
        generateAndFund(fundingAddrFile, fundingSkeyFile, network, name)
    else:
        generateAccount(network, name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-F', '--with-funding',
                        default=False,
                        dest='with_funding',
                        help='Do you want to provide a funding key to fund your new account?',
                        type=bool
                        )
    parser.add_argument('-L', '--lovelace-amount',
                        default=1000000,
                        dest='lovelace_amount',
                        help='Please provide the amount in lovelace to fund your new account',
                        type=str
                        )
    parser.add_argument(
        '-A', '--funding-addr-file',
        default='/home/christos/IOHK/repos/cardano-node/running_block_producer/mambaQAPool/payment.addr',
        dest='funding_addr_file',
        help='Provide location of funding address file.',
        type=str,
        )
    parser.add_argument(
        '-K', '--funding-skey-file',
        default='/home/christos/IOHK/repos/cardano-node/running_block_producer/mambaQAPool/payment.skey',
        dest='funding_skey_file',
        help='Provide location of funding skey file.',
        type=str,
        )
    parser.add_argument(
        '-N', '--network',
        default='mainnet',
        dest='network',
        help='Provide cardano network.',
        type=str
        )
    parser.add_argument(
        '--name',
        default='payment',
        dest='name',
        help='Base name for generated files (default: payment).',
        type=str
        )
    args = parser.parse_args()

    main(args.with_funding,
         args.lovelace_amount,
         args.funding_addr_file,
         args.funding_skey_file,
         args.network,
         args.name)
