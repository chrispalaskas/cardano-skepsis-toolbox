# This is a WIP and should be used with caution.
# There are no safety mechanisms in case of a failure.
# User should monitor the progress.


from multiprocessing import pool
import cardano_cli_helper as cli
import sendADA
import argparse
from os.path import exists
import os
import json
import time


def generateMetadataJSON(poolName, ticker):
    metaData = {
                    "name": poolName,
                    "description": f"Mamba test pool {poolName}",
                    "ticker": ticker,
                    "homepage": "https://github.com/chrispalaskas"
                }
    filename = f'{poolName}-metadata.json'
    with open(filename, 'w') as metadataFile:
        json.dump(metaData, metadataFile, indent=4, sort_keys=False)
    return cli.getHashOfMetadataJSON(filename)


def main(fundingAddrFile, fundingSkeyFile, poolName, poolTicker, network='mainnet'):
    pool_deposit = 500000000
    min_amount = 1000000
    working_folder = os.getcwd()
    if not exists(fundingAddrFile):
        print('ERROR: Funding address file does not exist.')
        return 0
    if not exists(fundingSkeyFile):
        print('ERROR: Funding skey file does not exist.')
        return 0

    cli.getProtocolJson(network)
    cli.generatePaymentKeyPair()
    cli.generateStakeKeyPair()
    cli.generatePaymentAddress(network)
    with open('payment.addr') as addr_file:
        paymentAddr = addr_file.read().strip()
    paymentSkeyFile = 'payment.skey'
    cli.generateStakeAddress(network)
    cli.createRegistrationCertificate()

    # Fund newly created account
    sendADA.main(fundingAddrFile,
                 fundingSkeyFile,
                 os.path.join(working_folder, 'payment.addr'),
                 3750000000,
                 network)
    lovelace = -1
    while lovelace == -1:
        print('Waiting for Tx to get on the blockchain')
        time.sleep(5)
        lovelace, utxos = cli.getLovelaceBalance(paymentAddr, network)
    ttlSlot = cli.queryTip('slot', network) + 1000
    cli.buildRegisterCertTx(utxos[0], ttlSlot, min_amount, network)
    cli.signTx([paymentSkeyFile, 'stake.skey'], network=network)
    cli.submitSignedTx(network=network)
    newLovelace = lovelace
    while lovelace == newLovelace:
        print('Waiting for Tx to get on the blockchain')
        time.sleep(5)
        newLovelace, utxos = cli.getLovelaceBalance(paymentAddr, network)
    cli.generateVRFKeyPair()
    cli.generateColdKeys()
    cli.generateKESKeyPair()
    print('Generated keys')
    slotsPerKESPeriod=86400
    cli.generateOperationalCertificate(slotsPerKESPeriod=slotsPerKESPeriod, network=network)
    print('Generated certificate')
    metadataHash = generateMetadataJSON(poolName, poolTicker).strip()
    print('Generated metadata')
    # TODO: post on github gist, generate URL
    # This URL is wrong but it will show a different address in db-sync to ease identification
    metadataURL = f'https://example.com/{poolTicker}'
    cli.generateStakePoolRegistrationCertificate(100000000, '0.0.0.0', metadataURL, metadataHash, network=network)
    cli.generateDelegationCertificatePledge()
    print('Generated delegation certificate pledge')
    lovelace, utxos = cli.getLovelaceBalance(paymentAddr, network)
    ttlSlot = cli.queryTip('slot', network) + 1000
    cli.buildPoolAndDelegationCertTx(utxos[0], ttlSlot, min_amount, network)
    cli.signTx(['payment.skey', 'stake.skey', 'cold.skey'], network=network)
    cli.submitSignedTx(network=network)
    newLovelace = lovelace
    while lovelace == newLovelace:
        print('Waiting for Tx to get on the blockchain')
        time.sleep(5)
        newLovelace, utxos = cli.getLovelaceBalance(paymentAddr, network)
    poolId = cli.getPoolId().strip()
    print('Pool registered:', cli.verifyPoolIsRegistered(poolId, network))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--funding-addr-file',
                    dest='funding_addr_file',
                    help='Provide location of funding address file.',
                    type=str,
                    required=True
                    )
    parser.add_argument('-K', '--funding-skey-file',
                    dest='funding_skey_file',
                    help='Provide location of funding skey file.',
                    type=str,
                    required=True
                    )
    parser.add_argument('-N', '--network',
                    default='testnet-magic 9',
                    dest='network',
                    help='Provide cardano network.',
                    type=str
                    )
    parser.add_argument('--name',
                    dest='name',
                    help='Pool name.',
                    type=str,
                    required=True
                    )
    parser.add_argument('--ticker',
                    dest='ticker',
                    help='Pool ticker.',
                    type=str,
                    required=True
                    )

    args = parser.parse_args()

    main(args.funding_addr_file,
         args.funding_skey_file,
         args.name,
         args.ticker,
         args.network)
