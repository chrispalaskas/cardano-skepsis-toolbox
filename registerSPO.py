# This is a WIP and should be used with caution.
# There are no safety mechanisms in case of a failure.
# User should monitor the progress.


import cardano_cli_helper as cli
import sendTokens
import argparse
from os.path import exists
import os
import json
import time
import re


def generateMetadataJSON(poolName, ticker, homepage):
    metaData = {
                    "name": poolName,
                    "description": f"Partner chains test pool {poolName}",
                    "ticker": ticker,
                    "homepage": homepage
                }
    filename = f'{poolName}-metadata.json'
    with open(filename, 'w') as metadataFile:
        json.dump(metaData, metadataFile, indent=4, sort_keys=False)
    return cli.getHashOfMetadataJSON(filename)


def main(fundingAddrFile, fundingSkeyFile, poolName, poolTicker, homepage,
         fund_amount, pledge_amount, pool_ip, network, era):
    if not exists(poolName):
        os.mkdir(poolName)
    else:
        print('Destination folder already exists. Please delete or rename.')
        return
    os.chdir(poolName)
    ticker_pattern = re.search('^[A-Z0-9]+$', poolTicker)
    if len(poolTicker) < 3 or len(poolTicker) > 5:
        print('ERROR: Ticker should be between 3 and 5 characters')
        exit(-1)
    if ticker_pattern is None or ticker_pattern.string != poolTicker:
        print('ERROR: Ticker should contain only uppercase letters and digits')
        exit(-1)
    if fund_amount <= pledge_amount + 4000000:  # TODO: be more precise?
        print('ERROR: Funding will not be enough for pledge \
              and network fees for all operations')
        exit(-1)
    min_amount = 1000000
    working_folder = os.getcwd()
    if not exists(fundingAddrFile):
        print('ERROR: Funding address file does not exist.')
        return 0
    if not exists(fundingSkeyFile):
        print('ERROR: Funding skey file does not exist.')
        return 0

    cli.generatePaymentKeyPair()
    cli.generateStakeKeyPair()
    cli.generatePaymentAddressForStaking(network)
    with open('payment.addr') as addr_file:
        paymentAddr = addr_file.read().strip()
    paymentSkeyFile = 'payment.skey'
    cli.generateStakeAddress(network)
    cli.createRegistrationCertificate(era)

    # Fund newly created account
    # TODO: Verify the funding account has enough funds
    print(f'funding address {paymentAddr}')
    sendTokens.main(
        fundingAddrFile,
        fundingSkeyFile,
        os.path.join(working_folder, 'payment.addr'),
        fund_amount,
        [],
        [],
        network=network,
        era=era
        )
    lovelace = -1
    while lovelace == -1:
        print('Getting address initial UTxOs')
        time.sleep(5)
        lovelace, utxos = cli.getLovelaceBalance(
            paymentAddr, network, onlyAda=True
            )
    ttlSlot = cli.queryTip('slot', network) + 1000
    cli.buildCertificateFileListTx(
        ['stake.cert'], paymentAddr, utxos, ttlSlot, amount=min_amount,
        network=network, era=era
        )
    cli.signTx([paymentSkeyFile, 'stake.skey'], network=network)
    cli.submitSignedTx(network=network)
    newLovelace = lovelace
    while lovelace == newLovelace:
        print('Waiting for stake certificate Tx to get on the blockchain')
        time.sleep(5)
        newLovelace, utxos = cli.getLovelaceBalance(
            paymentAddr, network, onlyAda=True
            )
    cli.generateVRFKeyPair()
    cli.generateColdKeys()
    cli.generateKESKeyPair()
    print('Generated keys')
    slotsPerKESPeriod = 86400
    cli.generateOperationalCertificate(
        slotsPerKESPeriod=slotsPerKESPeriod, network=network
        )
    print('Generated certificate')
    metadataHash = generateMetadataJSON(poolName, poolTicker, homepage).strip()
    print('Generated metadata')
    # TODO: post on github gist, generate URL
    # This URL is wrong but it will show a different address
    # in db-sync to ease identification
    metadataURL = f'https://example.com/{poolTicker}'
    cli.generateStakePoolRegistrationCertificate(
        pledge_amount, pool_ip, metadataURL, metadataHash, era, network=network
        )
    cli.generateDelegationCertificatePledge(era)
    print('Generated delegation certificate pledge')
    lovelace, utxos = cli.getLovelaceBalance(
        paymentAddr, network, onlyAda=True
        )
    ttlSlot = cli.queryTip('slot', network) + 1000
    cli.buildCertificateFileListTx(
        ['pool-registration.cert', 'delegation.cert'], paymentAddr,
        utxos, ttlSlot, amount=min_amount, network=network, era=era
        )
    cli.signTx(['payment.skey', 'stake.skey', 'cold.skey'], network=network)
    cli.submitSignedTx(network=network)
    newLovelace = lovelace
    while lovelace == newLovelace:
        print('Waiting for pool registration and delegation certificates '
              'Tx to get on the blockchain')
        time.sleep(5)
        newLovelace, utxos = cli.getLovelaceBalance(
            paymentAddr, network, onlyAda=True
            )
    poolId = cli.getPoolId().strip()
    with open('pool_id.txt', 'w') as poolIdFile:
        poolIdFile.write(poolId)

    print('Pool registered:', cli.verifyPoolIsRegistered(poolId, network))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-A', '--funding-addr-file',
        dest='funding_addr_file',
        help='Provide location of funding address file.',
        type=str,
        default='/home/christos/IOHK/Cardano_configs/preprod_run/keys/payment.addr'
        )
    parser.add_argument(
        '-K', '--funding-skey-file',
        dest='funding_skey_file',
        help='Provide location of funding skey file.',
        type=str,
        default='/home/christos/IOHK/Cardano_configs/preprod_run/keys/payment.skey'
        )
    parser.add_argument(
        '-N', '--network',
        default='testnet-magic 1',
        dest='network',
        help='Provide cardano network.',
        type=str
        )
    parser.add_argument(
        '--name',
        dest='name',
        help='Pool name.',
        type=str,
        default='PC_Staging7'
        )
    parser.add_argument(
        '--ticker',
        dest='ticker',
        help='Pool ticker. Should be between 3 and 5 uppercase \
            characters or numbers.',
        type=str,
        default='PCS7'
        )
    parser.add_argument(
        '--homepage',
        default="https://github.com/chrispalaskas",
        dest='homepage',
        help='Pool homepage.',
        type=str
        )
    parser.add_argument(
        '--fund-amount',
        default=2504*10**6,
        dest='fund_amount',
        help='Amount to fund the new account with, in lovelace. The pledge will be subtracted from this amount.',
        type=int
        )
    parser.add_argument(
        '--pledge-amount',
        default=500*10**6,
        dest='pledge_amount',
        help='Amount of pledge in lovelace.',
        type=int
        )
    parser.add_argument(
        '--pool-ip',
        default='0.0.0.0',
        dest='pool_ip',
        help='IP of pool to register.',
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

    main(args.funding_addr_file,
         args.funding_skey_file,
         args.name,
         args.ticker,
         args.homepage,
         args.fund_amount,
         args.pledge_amount,
         args.pool_ip,
         args.network,
         args.era)
