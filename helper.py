from multiprocessing import pool
import requests
import json, collections
import shutil
from os.path import exists
import cardano_cli_helper as cli
import time

def getBlockfrostAPIData(requestString: str, apiKey: str):
    header = {"project_id":apiKey}
    # Get call from blockfrost.io
    for i in range(10):
        data = requests.get(requestString, headers=header)
        if (data.status_code == 200):
            break
        print('Request failed, retrying...', i+1)
        time.sleep(6)
    if (data.status_code != 200):
        print('Error: Request failed: ', requestString)
        return False
    try:
        dataJson = json.loads(data.text)
        return dataJson
    except:
        print('Error: Request return not in JSON format')
        return False


def getRecipientsFromStakeAddr(stakeAddressesOfRecipients: list, recipientList: list, blockfrostURL: str, apiKey: str):
    # Convert staking address list to sending address list
    for stakeAddr in stakeAddressesOfRecipients:
        requestString = blockfrostURL + 'accounts/' + stakeAddr + '/addresses'
        addressJson = getBlockfrostAPIData(requestString, apiKey)
        # Use first address from the returned list 
        try:
            delegatorAddr = addressJson[0]['address']
            recipientList.append(delegatorAddr)
        except:
            print('Error: Key address not found.')
    return recipientList


def getSenderAddressFromTxHash(txHash: str, blockfrostURL: str, apiKey: str):
    txHash=txHash.split('#')[0] # Drop the TxId
    requestString = blockfrostURL + 'txs/' + txHash + '/utxos'
    txhashJson = getBlockfrostAPIData(requestString, apiKey)
    try:
        senderAddress = txhashJson['inputs'][0]['address']
        return senderAddress
    except:
        print('Error: Key inputs or address not found.')
        return False


def appendLogJson(logfile: str, data: dict):
    try:
        with open(logfile, 'r') as jsonlog:
            old_data = json.load(jsonlog)
    except:
        if exists(logfile):
            print('Logfile not loaded properly. Backing up and creating a new one.')
            shutil.copyfile(logfile, logfile + '.bk')
        else:
            print('Logfile does not exist. Creating a new one.')
        old_data = {}
    if old_data == {}:
        newDict = data
    else:
        newDict = {**old_data, **data}
    reverseNewDict = collections.OrderedDict(reversed(newDict.items())) # if you want reversed sorted
    with open(logfile, 'w') as jsonlog:
        json.dump(reverseNewDict, jsonlog, indent=4, sort_keys=False)
        print('Log appended')


def parseConfigSendAssets(configFile, stakeAddressesOfRecipients, recipientList):
    finRecipientObjList = []
    try:
        with open(configFile, 'r') as jsonConfig:
            print('Opened config file...')
            config = json.load(jsonConfig)
            myPaymentAddrFile = config['myPaymentAddrFile']
            myPaymentAddrSignKeyFile = config['myPaymentAddrSignKeyFile']
            tokenPolicyID = config['tokenPolicyID']
            noOfTokensToSend = config['noOfTokensToSend']
            minADAToSendWithToken = config['minADAToSendWithToken']
            sentTokensLogFile = config['sentTokensLogFile']
            delegatorsLogFile = config['delegatorsLogFile']
            minFee = config['minFee']
            blockfrostURL = config['blockFrostURL']
            blockFrostProjID = config['blockFrostProjID']
            recipientList = getRecipientsFromStakeAddr(stakeAddressesOfRecipients, recipientList, blockfrostURL, blockFrostProjID)
            for recipientAddr in recipientList:
                finRecipientObjList.append(cli.Recipient(recipientAddr, 0, minADAToSendWithToken, noOfTokensToSend))
            print('Config file parsed succesfully!')
            return myPaymentAddrFile, \
                   myPaymentAddrSignKeyFile, \
                   tokenPolicyID, \
                   sentTokensLogFile, \
                   delegatorsLogFile, \
                   minFee, \
                   finRecipientObjList
    except:
        print('Configuration file misformated or does not exist.')
        return False


def parseConfigMonitorAddr(configFile):
    try:
        with open(configFile, 'r') as jsonConfig:
            print('Opened config file...')
            config = json.load(jsonConfig)
            myPaymentAddrFile = config['myPaymentAddrFile']
            myPaymentAddrSignKeyFile = config['myPaymentAddrSignKeyFile']
            tokenPolicyID = config['tokenPolicyID']
            tokenPriceLovelace = config['tokenPriceLovelace']
            stakingTokenRatio = config['stakingTokenRatio']
            minADAToSendWithToken = config['minADAToSendWithToken']
            minFee = config['minFee']
            incomingTxhashLogFile = config['incomingTxhashLogFile']
            sentTxhashLogFile = config['sentTxhashLogFile']
            sentTokensLogFile = config['sentTokensLogFile']
            delegatorsLogFile = config['delegatorsLogFile']
            blockFrostURL = config['blockFrostURL']
            blockFrostProjID = config['blockFrostProjID']
            print('Config file parsed succesfully!')
            return myPaymentAddrFile, \
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
                   blockFrostProjID
    except:
        print('Configuration file misformated or does not exist.')
        return False


def parseConfigGetDelegators(configFile):
    try:
        with open(configFile, 'r') as jsonConfig:
            print('Opened config file...')
            config = json.load(jsonConfig)
            delegatorsLogFile = config['delegatorsLogFile']
            blockFrostURL = config['blockFrostURL']
            blockFrostProjID = config['blockFrostProjID']
            poolID = config['poolID']
            koiosURL = config['koiosURL']
            print('Config file parsed succesfully!')
            return delegatorsLogFile, \
                   blockFrostURL, \
                   blockFrostProjID, \
                   koiosURL, \
                   poolID
    except:
        print('Configuration file misformated or does not exist.')
        return False


def calculateSoldTokensToSend(lovelace_received, minADAToSendWithToken, minFee, tokenPriceLovelace):
    # Calculates how many tokens to send when selling them at a specific price
    tokens_to_send = int((lovelace_received - minADAToSendWithToken - minFee) / tokenPriceLovelace)
    if tokens_to_send<0:
        tokens_to_send = 0
    lovelace_amount_to_refund = lovelace_received - (tokens_to_send * tokenPriceLovelace) - minFee    
    return tokens_to_send, lovelace_amount_to_refund


def calculateEarnedTokensToSend(lovelace_received, minADAToSendWithToken, minFee, totalStakedAmount, stakingTokenRatio):
    # Calculates how many tokens to send for a specific delegator
    tokens_to_send = round(totalStakedAmount * stakingTokenRatio)
    if tokens_to_send == 0:
        lovelace_amount_to_refund = lovelace_received - minFee
    else:
        lovelace_amount_to_refund = minADAToSendWithToken
    # Sanity Check
    if lovelace_received < minADAToSendWithToken + minFee:
        tokens_to_send = 0
        lovelace_amount_to_refund = lovelace_received - minFee
    return tokens_to_send, lovelace_amount_to_refund


def getDelegatorsBlockfrost(pool_id, blockfrostURL: str, apiKey: str):
    # Get list of delegators from a Pool
    requestString = blockfrostURL + 'pools/' + pool_id + '/delegators'
    print (requestString)
    delegatorsList = getBlockfrostAPIData(requestString, apiKey)
    delegators = {}
    try:
        for deleg in delegatorsList:
            delegators[deleg['address']] = int(deleg['live_stake'])
    except:
        print('Error: Not a proper JSON return.')
    return delegators



def getDelegatorsKoios(pool_id, URL: str, epoch: int):
    # Get list of delegators from a Pool
    requestString = URL + 'pool_delegators'
    params = {"_pool_bech32":pool_id, "_epoch_no": str(epoch)}

    print ('requestString', requestString)

    # Get call from api.koios.rest
    data = requests.get(requestString, params=params)
    if (data.status_code != 200):
        print('Error: Request failed: ', requestString)
        return False
    try:
        dataJson = json.loads(data.text)
    except:
        print('Error: Request return not in JSON format')
        return False

    delegatorsList = dataJson
    delegators = {}
    try:
        for deleg in delegatorsList:
            delegators[deleg['stake_address']] = int(deleg['amount'])
    except:
        print('Error: Not a proper JSON return.')
    return delegators


def getCurrentEpoch(blockfrostURL: str, apiKey: str):
    # Get current epoch
    requestString = blockfrostURL + 'epochs/latest'
    data = getBlockfrostAPIData(requestString, apiKey)
    epoch = 0
    try:
        epoch = data['epoch']
    except:
        print('Error: Not a proper JSON return.')
    return epoch


def getStakeFromAddress(paymentAddr: str, blockfrostURL: str, apiKey: str):
    # Get Staking address of payment address
    requestString = blockfrostURL + 'addresses/' + paymentAddr
    data = getBlockfrostAPIData(requestString, apiKey)
    try:
        stakeAddr = data['stake_address']
        return stakeAddr
    except:
        print('Error: could not find stake_address key in response')
        return False