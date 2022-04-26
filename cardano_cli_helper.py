import json
from subprocess import PIPE, Popen
from os.path import exists
from datetime import datetime
import subprocess
import select


class Recipient:
    address = str
    stake_address = str
    lovelace_amount_received = int
    lovelace_amount_to_send = int
    token_amount_to_send = int

    def __init__(self, addr, stake_addr, lovelace_in, lovelace_out, tokens_out):
        self.address = addr
        self.stake_address = stake_addr
        self.lovelace_amount_received = lovelace_in
        self.lovelace_amount_to_send = lovelace_out
        self.token_amount_to_send = tokens_out


def getCardanoCliValue(command, key):
    with Popen(command, stdout=PIPE, stderr=PIPE, shell=True) as process:
        stdout, stderr = process.communicate()
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        print(stdout)
        print(stderr)
        if not stderr == '':
            return (-1)
    if not key == '':
        try:
            result = json.loads(stdout)[key]
            return result
        except:
            print('Error: Request return not in JSON format or key ', key, ' doesn\'t exist')
            return(-1)
    return stdout


def getLovelaceBalance(addr):
    print('Getting address\' balance in lovelace...')
    utxos = getAddrUTxOs(addr)
    dict = getTokenListFromTxHash(utxos)
    keys = list(utxos.keys())
    return dict['ADA'], keys


def getStakeBalance(stake_addr):
    command = f'cardano-cli query stake-address-info --cardano-mode --address {stake_addr} --mainnet'
    res = eval(getCardanoCliValue(command, ''))
    return res[0]['rewardAccountBalance']


def getAddrUTxOs(addr):
    print('Getting address\' transactions...')
    outfile = 'utxos.json'
    command = f'cardano-cli query utxo --address {addr} --mainnet --out-file {outfile}'
    if getCardanoCliValue(command, '') != -1:
        file = open(outfile)
        utxosJson = json.load(file)
        file.close()
        return utxosJson
    else:
        return False


def getTxInWithLargestTokenAmount(utxosJson, tokenPolicyID):
    tokenMax = 0
    maxTokenTxHash = str
    for key in utxosJson.keys():
        for key2 in utxosJson[key]['value'].keys():
            if key2 == 'lovelace':
                continue
            else:
                for key3 in utxosJson[key]['value'][key2].keys():
                    if key2+'.'+key3 == tokenPolicyID:
                        if tokenMax < utxosJson[key]['value'][key2][key3]:
                            tokenMax = utxosJson[key]['value'][key2][key3]
                            maxTokenTxHash = key
    return maxTokenTxHash


def getTokenListFromTxHash(utxosJson):
    print('Getting list of tokens and ADA with amounts...')
    tokensDict = {}
    for key in utxosJson.keys():
        for key2 in utxosJson[key]['value'].keys():
            if key2 == 'lovelace':
                if 'ADA' in tokensDict.keys():
                    tokensDict['ADA'] += utxosJson[key]['value'][key2]
                else:
                    tokensDict['ADA'] = utxosJson[key]['value'][key2]
            else:
                for key3 in utxosJson[key]['value'][key2].keys():
                    if key2+'.'+key3 in tokensDict.keys():
                        tokensDict[key2+'.'+key3] += utxosJson[key]['value'][key2][key3]
                    else:
                        tokensDict[key2+'.'+key3] = utxosJson[key]['value'][key2][key3]
    return tokensDict


def getForeignTokensFromTokenList(tokensDict: dict, tokenPolicyID: str):
    print('Getting list of foreign tokens received with amounts...')
    foreignTokensDict = tokensDict.copy()
    foreignTokensDict.pop('ADA', None)
    foreignTokensDict.pop(tokenPolicyID, None)
    return foreignTokensDict


def getProtocolJson():
    if not exists('protocol.json'):
        print('Getting protocol.json...')
        command = 'cardano-cli query protocol-parameters --mainnet --out-file protocol.json'
        return getCardanoCliValue(command, '')
    else:
        print ('Protocol file found.')
        return


def getCurrentSlot():
    print('Getting current slotNo...')
    command = f'cardano-cli query tip --mainnet'
    return getCardanoCliValue(command, 'slot')


def getMinFee(txInCnt, txOutCnt):
    print('Getting min fee for transaction...')
    txOutCnt += 1
    witness_count = 1
    command = f'cardano-cli transaction calculate-min-fee \
                                --tx-body-file tx.tmp \
                                --tx-in-count {txInCnt} \
                                --tx-out-count {txOutCnt} \
                                --mainnet \
                                --witness-count {witness_count} \
                                --byron-witness-count 0 \
                                --protocol-params-file protocol.json'
    feeString = getCardanoCliValue(command, '')
    print(feeString)
    return int(feeString.split(' ')[0])


def getDraftTX(txInList, returnAddr, recipientList, ttlSlot):
    print('Creating tx.tmp...')
    command = f'cardano-cli transaction build-raw \
                --fee 0 '
    for txIn in txInList:
        command += f'--tx-in {txIn} '
    # The recipient is of class Recipient (address, lovelace in, lovelace out, token out)
    for recipient in recipientList:
        command += f'--tx-out {recipient.address}+0 '
    command += f'--tx-out {returnAddr}+0 \
                 --invalid-hereafter {ttlSlot} \
                 --out-file tx.tmp'
    getCardanoCliValue(command, '')
    return


def getDraftTXSimple(txInList, returnAddr, recipientAddr, ttlSlot):
    print('Creating simple tx.tmp...')
    command = f'cardano-cli transaction build-raw \
                --fee 0 '
    for txIn in txInList:
        command += f'--tx-in {txIn} '
    command += f'--tx-out {recipientAddr}+0 '
    command += f'--tx-out {returnAddr}+0 \
                 --invalid-hereafter {ttlSlot} \
                 --out-file tx.tmp'
    getCardanoCliValue(command, '')
    print('here')
    return


def getRawTxSimple(txInList, returnAddr, recipientAddr, lovelace_amount, lovelace_return, ttlSlot, fee):
    print('Creating simple tx.raw...')
    command = f'cardano-cli transaction build-raw \
                --fee {fee} '
    for txIn in txInList:
        command += f'--tx-in {txIn} '
    command += f'--tx-out {recipientAddr}+{lovelace_amount} '
    command += f'--tx-out {returnAddr}+{lovelace_return} '
    command += f'--invalid-hereafter {ttlSlot} \
                 --out-file tx.raw'
    getCardanoCliValue(command, '')


def getRawTx(txInList, initLovelace, initToken, returnAddr, recipientList, ttlSlot, fee, minFee, tokenPolicyId, foreignTokensDict):
    print('Creating tx.raw...')
    lovelace_received = 0
    lovelace_to_send = 0
    tokens_to_send = 0
    fees_withheld = 0
    # The recipient is of class Recipient (address, lovelace in, lovelace out, token out)
    for recipient in recipientList:
        lovelace_received += recipient.lovelace_amount_received
        lovelace_to_send += recipient.lovelace_amount_to_send
        tokens_to_send += recipient.token_amount_to_send
        fees_withheld += minFee

    lovelace_to_return = initLovelace - fee - lovelace_to_send
    tokens_to_return = initToken - tokens_to_send
    print('adaToSend: ', lovelace_to_send)
    print('tokensToSend: ', tokens_to_send)
    print('adaToReturn: ', lovelace_to_return)
    print('tokensToReturn: ', tokens_to_return)
    command = f'cardano-cli transaction build-raw \
                --fee {fee} '
    for txIn in txInList:
        command += f'--tx-in {txIn} '
    for recipient in recipientList:
        command += f'--tx-out {recipient.address}+{recipient.lovelace_amount_to_send}+"{recipient.token_amount_to_send} {tokenPolicyId}" ' 
    command += f'--tx-out {returnAddr}+{lovelace_to_return}+"{tokens_to_return} {tokenPolicyId}"'
    for key in foreignTokensDict: # Send all other incoming tokens too
        command += f'+"{foreignTokensDict[key]} {key}"'
    command += f' --invalid-hereafter {ttlSlot} \
                 --out-file tx.raw'
    getCardanoCliValue(command, '')


def signTx(myPaymentAddrSignKeyFile):
    print('Signing Transaction...')
    command = f'cardano-cli transaction sign \
                    --signing-key-file {myPaymentAddrSignKeyFile} \
                    --tx-body-file tx.raw \
                    --out-file tx.signed \
                    --mainnet'
    getCardanoCliValue(command, '')


def submitSignedTx(signed_file='tx.signed'):
    print('Submitting Transaction...')
    command = f'cardano-cli transaction submit --tx-file {signed_file} --mainnet'
    return getCardanoCliValue(command, '')


def sendTokenToAddr(myPaymentAddrSignKeyFile: str, txInList: list, initLovelace: int, initToken: int,
                    fromAddr: str, recipientList: list, tokenPolicyId: str, minFee: int, foreignTokensDict: dict):
    ttlSlot = getCurrentSlot() + 2000
    print('TTL Slot:', ttlSlot)
    getDraftTX(txInList, fromAddr, recipientList, ttlSlot)
    fee = getMinFee(len(txInList), len(recipientList))
    print ('Min fee:', fee)
    getRawTx(txInList, initLovelace, initToken, fromAddr, recipientList, ttlSlot, fee, minFee, tokenPolicyId, foreignTokensDict)
    signTx(myPaymentAddrSignKeyFile)
    # return submitSignedTx()


def getCnodeJournal(paymentAddr, tokenPolicyId, myTxHash):
    # Print the current time to estimate how long it will take
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print('Transaction submitted at ' + current_time + '.')
    print('Waiting for a block to include the transaction...')

    args = ['journalctl', '--lines', '0', '--follow', '_SYSTEMD_UNIT=cnode.service']
    f = subprocess.Popen(args, stdout=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)
    blocksCnt = 0
    while True:
        if p.poll(100):
            line = f.stdout.readline().strip()
            if "Chain extended" in str(line):
                print ('New block arrived!')
                blocksCnt += 1
                utxosNew = getAddrUTxOs(paymentAddr)
                myTxHashNew = getTxInWithLargestTokenAmount(utxosNew, tokenPolicyId)
                if myTxHash != myTxHashNew:
                    timediff = datetime.now() - now
                    print ('Transaction succesfully recorded on blockchain in ', timediff, ' after ', blocksCnt, ' blocks.')
                    return True
                print ('Waiting for the next block to include the transaction...')
                print ('Ctrl-C to exit. Will NOT cancel the transaction but will skip logging of completion.')


def getRawTxStakeWithdraw(tx_in, payment_addr, stake_addr):
    command = f'cardano-cli transaction build-raw \
                --tx-in {tx_in} \
                --tx-out {payment_addr}+0 \
                --withdrawal {stake_addr}+0 \
                --invalid-hereafter 0 \
                --fee 0 \
                --out-file tx.tmp'
    getCardanoCliValue(command, '')


def buildRawTxStakeWithdraw(tx_in, payment_addr, withdrawal, stake_addr, stake_rewards, minFee):
    currentSlot = getCurrentSlot()
    command = f'cardano-cli transaction build-raw \
                --tx-in {tx_in} \
                --tx-out {payment_addr}+{withdrawal} \
                --withdrawal {stake_addr}+{stake_rewards} \
                --invalid-hereafter {currentSlot+1000} \
                --fee {minFee} \
                --out-file withdraw_rewards.raw'
    getCardanoCliValue(command, '')


def signTxStakeWithdraw(myPaymentSkeyFile, stakeSkeyFile):
    print('Signing stake withdraw TX')
    command = f'cardano-cli transaction sign \
                --tx-body-file withdraw_rewards.raw  \
                --signing-key-file {myPaymentSkeyFile} \
                --signing-key-file {stakeSkeyFile} \
                --out-file withdraw_rewards.signed'
    getCardanoCliValue(command, '')