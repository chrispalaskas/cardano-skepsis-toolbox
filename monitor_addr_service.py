import cardano_cli_helper as cli
import helper
import send_assets_to_recipients as sendAssets
import json
import time
from datetime import datetime
from os.path import exists
import os

MODE = 'marketplace' # 'delegators'

def main(network,
         myPaymentAddrFile,
         myPaymentAddrSignKeyFile,
         tokenPolicyID,
         tokenPriceLovelace,
         stakingTokenRatio,
         minADAToSendWithToken,
         minFee,
         incomingTxhashLogFile,
         sentTxhashLogFile,
         sentTokensLogFile,
         delegatorsLogFile,
         blockFrostURL,
         blockFrostProjID):
    if MODE not in ['marketplace', 'delegators']:
        print('ERROR: Supported modes: [marketplace, delegators]')
        exit(0)
    sent_utxos_set = set([])
    # Add the last known used (sent) txHash from the logfile
    if exists(sentTxhashLogFile):
        try:
            with open(sentTxhashLogFile, 'r') as jsonlog:
                old_sent_txhash = json.load(jsonlog)
                old_list = list(old_sent_txhash.keys())
                old_list.sort(reverse=True)
                sent_utxos_set.update(old_sent_txhash[old_list[0]])
        except:
            print('Logfile misformated. Backing up and starting new.')
            os.rename(sentTxhashLogFile, sentTxhashLogFile + '.bk')

    if exists(delegatorsLogFile):
        try:
            with open(delegatorsLogFile, 'r') as jsonData:
                delegatorsDict = json.load(jsonData)
        except:
            print('Delegators list file misformated.')
            return -1

    tokenRecipientList = [] # List of class Recipient objects (address, ada amount received, ada refund amount, tokens to send)

    with open(myPaymentAddrFile) as file:
        paymentAddr = file.read()
    while True:
        # Get your payment address TxHashes
        utxos = cli.getAddrUTxOs(paymentAddr,network=network)
        if not utxos:
            print('Error: Could not get address UTxOs. Please check network connection. Retrying in 30 seconds.')
            time.sleep(30)
            continue
        myTxHash = cli.getTxInWithLargestTokenAmount(utxos, tokenPolicyID)
        sent_utxos_set.add(myTxHash)
        # Store on log file
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        latest_utxo = {}
        latest_utxo[current_time] = list(utxos)
        sent_utxo = {}
        sent_utxo[current_time] = list(sent_utxos_set)
        new_utxos_set = set(utxos.keys())
        if (sent_utxos_set.issuperset(new_utxos_set)):
            print ('No incoming Tx, sleeping for 30 seconds...')
            time.sleep(30)
            continue
        helper.appendLogJson(incomingTxhashLogFile, latest_utxo)
        helper.appendLogJson(sentTxhashLogFile, sent_utxo)
        print('Incoming Tx detected!')
        diff_utxos = new_utxos_set.difference(sent_utxos_set)

        for new_utxo in diff_utxos:
            print('New Utxo: ', new_utxo)
            if not blockFrostURL == '' and not blockFrostProjID == '':
                address_received = helper.getSenderAddressFromTxHash(new_utxo, blockFrostURL, blockFrostProjID)
            else:
                # WARNING! Danger!!! Assuming simple incoming transaction, we can query ledger for next UTxO's change address
                address_received = cli.getSenderAddressFromSimpleTxHash(new_utxo, network).strip()

            if not address_received:
                continue
            print('Address received:', address_received)
            if address_received == paymentAddr:
                sent_utxos_set.add(new_utxo)
                continue
            lovelace_received = utxos[new_utxo]['value']['lovelace']
            # An attempt to send back very small amounts will fail, due to network parameters
            if lovelace_received < 1000000 + minFee:
                print('Donation received! Thank you!')
                sent_utxos_set.add(new_utxo)
                continue
            print('Amount received:', lovelace_received)
            if MODE == 'marketplace':
                tokens_to_send, lovelace_amount_to_refund = helper.calculateSoldTokensToSend(lovelace_received, minADAToSendWithToken, minFee, tokenPriceLovelace)
                tokenRecipientList.append(cli.Recipient(address_received, '', lovelace_received,
                                            lovelace_amount_to_refund, tokens_to_send))
            elif MODE == 'delegators':
                stakeAddrRecipient = helper.getStakeFromAddress(address_received, blockFrostURL, blockFrostProjID)
                if lovelace_received >= tokenPriceLovelace and stakeAddrRecipient in delegatorsDict['sum']:
                    tokens_to_send, lovelace_amount_to_refund = \
                        helper.calculateEarnedTokensToSend(lovelace_received, minADAToSendWithToken, minFee,
                                                        delegatorsDict['sum'][stakeAddrRecipient], stakingTokenRatio)
                    print('Tokens to send: ', tokens_to_send)
                    print('Lovelace amount to refund: ', lovelace_amount_to_refund)
                elif not stakeAddrRecipient in delegatorsDict['sum']:
                    tokens_to_send = 0
                    lovelace_amount_to_refund = lovelace_received - minFee
                    print('Stake address not delegated with our pool. Issuing refund...')
                else:
                    tokens_to_send, lovelace_amount_to_refund = \
                        helper.calculateSoldTokensToSend(lovelace_received, minADAToSendWithToken, minFee, tokenPriceLovelace)
                    print('Amount received not enough. Issuing refund...')
                tokenRecipientList.append(cli.Recipient(address_received, stakeAddrRecipient, lovelace_received,
                                                        lovelace_amount_to_refund, tokens_to_send))


        if sendAssets.main(network,
                           tokenRecipientList,
                           myPaymentAddrFile,
                           myPaymentAddrSignKeyFile,
                           tokenPolicyID,
                           sentTokensLogFile,
                           delegatorsLogFile,
                           minFee):
            for new_utxo in diff_utxos:
                sent_utxos_set.add(new_utxo)
            tokenRecipientList = []
            if MODE == 'delegators':
                with open(delegatorsLogFile, 'r') as jsonData:
                    delegatorsDict = json.load(jsonData)
        else:
            print('Unexpected error encountered, trying again...')


if __name__ == '__main__':
    print('Monitor an address for incoming payments.')
    configFile = './config.json'
    network, \
    myPaymentAddrFile, \
    myPaymentAddrSignKeyFile, \
    tokenPolicyID, \
    tokenPriceLovelace, \
    stakingTokenRatio, \
    minADAToSendWithToken, \
    minFee, \
    incomingTxhashLogFile, \
    sentTxhashLogFile, \
    sentTokensLogFile, \
    delegatorsLogFile, \
    blockFrostURL, \
    blockFrostProjID = helper.parseConfigMonitorAddr(configFile)

    main(network,
         myPaymentAddrFile,
         myPaymentAddrSignKeyFile,
         tokenPolicyID,
         tokenPriceLovelace,
         stakingTokenRatio,
         minADAToSendWithToken,
         minFee,
         incomingTxhashLogFile,
         sentTxhashLogFile,
         sentTokensLogFile,
         delegatorsLogFile,
         blockFrostURL,
         blockFrostProjID)