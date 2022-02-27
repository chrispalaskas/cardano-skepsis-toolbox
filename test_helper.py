from cmath import exp
from decimal import MIN_EMIN
import unittest
import helper
from os.path import exists
import os
import json

import cardano_cli_helper as cli

def readConfigFile():
    try:
        with open('./config.json', 'r') as jsonConfig:
            print('Opened config file...')
            config = json.load(jsonConfig)
            blockFrostURL = config['blockFrostURL']
            blockFrostProjID = config['blockFrostProjID']
            return blockFrostURL, blockFrostProjID
    except:
        print('Configuration file misformated or does not exist.')
        return '', ''


class TestGetStakeFromAddress(unittest.TestCase):

    def test_get_stake_from_address(self):
        # a = cli.Recipient('asdfsadfsdafdsa', 'stake1u8wsm38q7axhqswt45wdlsqd3r0n5spjht3qzrgj6u3ss4slthexn', 100, 10, 1)
        # delegatorsLogFile = '/home/christo/Documents/cardano-skepsis-toolbox/logs/delegators_stake_log.json'
        # with open(delegatorsLogFile, 'r') as jsonData:
        #     delegatorsDict = json.load(jsonData)
        # delegatorsDict['sum'][a.stake_address] = 0
        # with open(delegatorsLogFile, 'w') as jsonlog:
        #     json.dump(delegatorsDict, jsonlog, indent=4, sort_keys=False)
        my_stake_addr = 'stake1u8wsm38q7axhqswt45wdlsqd3r0n5spjht3qzrgj6u3ss4slthexn'
        my_payment_addr = 'addr1qx5trqazps96kt7539ye9cs65nu7kww0ttlgk7u8g3eadrkaphzwpa6dwpquhtgumlqqmzxl8fqr9whzqyx394erpptqq4rdxh'
        returned_stake_addr = helper.getStakeFromAddress(my_payment_addr, blockFrostURL, blockFrostProjID)
        self.assertEqual(my_stake_addr, returned_stake_addr)


class TestAppendLogJson(unittest.TestCase):

    def test_new_log_creation(self):
        test_dir = os.path.expanduser('~/skepsis_toolbox_test')
        if not exists(test_dir):
            os.mkdir(test_dir)
        testDict = {'test': 'nada'}
        testFilePath = os.path.join(test_dir,'logtest.json')
        if exists(testFilePath):
            os.remove(testFilePath) 
        helper.appendLogJson(testFilePath,testDict)
        with open(testFilePath, 'r') as logfile:
            old_data = json.load(logfile)
        self.assertEqual(testDict, old_data)
        os.remove(testFilePath)
        os.rmdir(test_dir)


    def test_append_log(self):
        test_dir = os.path.expanduser('~/temp')
        if not exists(test_dir):
            os.mkdir(test_dir)
        testDict1 = {'test': 'nada'}
        testDict2 = {'foo': 'bar'}
        testDictAppended = { 'test': 'nada', 'foo': 'bar'}
        testFilePath = os.path.join(test_dir,'logtest.json')
        if exists(testFilePath):
            os.remove(testFilePath) 
        helper.appendLogJson(testFilePath,testDict1)
        helper.appendLogJson(testFilePath,testDict2)
        with open(testFilePath, 'r') as logfile:
            old_data = json.load(logfile)
        self.assertEqual(testDictAppended, old_data)
        os.remove(testFilePath)
        os.rmdir(test_dir)
        

class TestGetRecipientsFromStakeAddr(unittest.TestCase):
    def test_request(self):
        stakeAddrList = [
            'stake1u9unh8dunl2mj2pwdqm53k7xw4l7p9l2l4egywrdyqwhvnqyd7sx8',
            'stake1u9tgg8ej9pkxyac8g37h7f2ltl492qagwpur7nzmm7s78hcc9vycr'
        ]
        addrList = [
            'addr1v86pqugsjsu3enxnxxl9ky8g6eefvddtzvyted4mv0pwuysfj0zhz'
        ]
        expectedAddrList = [
            'addr1qxznj7tx2m26t3adaq73rc3xk66p7yhpra054pftlzeda5ne8wwme874hy5zu6phfrduvatluzt74ltjsgux6gqawexqmc4u25',
            'addr1v86pqugsjsu3enxnxxl9ky8g6eefvddtzvyted4mv0pwuysfj0zhz',
            'addr1qy69sldc5r6tz6ldrz26tkuxq9x5mthx3ujauk3gax6k892kss0ny2rvvfmsw3ra0uj47hl225p6surc8ax9hhapu00srken9j'
        ]
        newAddrList = helper.getRecipientsFromStakeAddr(stakeAddrList, addrList, blockFrostURL, blockFrostProjID)
        self.assertCountEqual(newAddrList, expectedAddrList)


    def test_wrong_input(self):
        stakeAddrList = [
            'haha12345',
            'whatstakeaddress?'
        ]
        newAddrList = helper.getRecipientsFromStakeAddr(stakeAddrList, [], blockFrostURL, blockFrostProjID)
        self.assertEqual(newAddrList, [])

class TestGetSenderAddressFromTxHash(unittest.TestCase):
    def test_request(self):
        knownSender = 'addr1v86pqugsjsu3enxnxxl9ky8g6eefvddtzvyted4mv0pwuysfj0zhz'
        knownHash = '9d9dc0fcc51f0646fbf5742c02f004d266dc7badac259f71b36e23774cc5d1e1#0'
        senderAddress = helper.getSenderAddressFromTxHash(knownHash, blockFrostURL, blockFrostProjID)
        self.assertEqual(knownSender, senderAddress)


    def test_wrong_input(self):
        knownHash = 'blahfoobarnada12345'
        senderAddress = helper.getSenderAddressFromTxHash(knownHash, blockFrostURL, blockFrostProjID)
        self.assertFalse(senderAddress)

class TestCalculateTokensToSend(unittest.TestCase):
    minADAToSendWithToken = 1444443
    minFee = 200000


    def test_calculate_refund_all(self):
        lovelace_received = 2000000
        tokenPriceLovelace = 1800000
        tokens_to_send, lovelace_amount_to_refund = \
            helper.calculateSoldTokensToSend(lovelace_received, self.minADAToSendWithToken, self.minFee, tokenPriceLovelace)
        self.assertEqual(tokens_to_send, 0)
        self.assertEqual(lovelace_amount_to_refund, lovelace_received - self.minFee)


    def test_calculate_send_one(self):
        lovelace_received = 3000000 + self.minADAToSendWithToken + self.minFee
        tokenPriceLovelace = 3000000
        tokens_to_send, lovelace_amount_to_refund = \
            helper.calculateSoldTokensToSend(lovelace_received, self.minADAToSendWithToken, self.minFee, tokenPriceLovelace)
        self.assertEqual(tokens_to_send, 1)
        self.assertEqual(lovelace_amount_to_refund, self.minADAToSendWithToken)


    def test_calculate_send_one_cheap(self):
        lovelace_received = 10 + self.minADAToSendWithToken + self.minFee
        tokenPriceLovelace = 10
        tokens_to_send, lovelace_amount_to_refund = \
            helper.calculateSoldTokensToSend(lovelace_received, self.minADAToSendWithToken, self.minFee, tokenPriceLovelace)
        self.assertEqual(tokens_to_send, 1)
        self.assertEqual(lovelace_amount_to_refund, self.minADAToSendWithToken)


    def test_calculate_send_many_cheap(self):
        lovelace_received = 3000000 + self.minADAToSendWithToken + self.minFee
        tokenPriceLovelace = 10
        tokens_to_send, lovelace_amount_to_refund = \
            helper.calculateSoldTokensToSend(lovelace_received, self.minADAToSendWithToken, self.minFee, tokenPriceLovelace)
        self.assertEqual(tokens_to_send, 300000)
        self.assertEqual(lovelace_amount_to_refund, self.minADAToSendWithToken)


    def test_calculate_send_many_cheap_with_refund(self):
        lovelace_received = 3000005 + self.minADAToSendWithToken + self.minFee
        tokenPriceLovelace = 10
        tokens_to_send, lovelace_amount_to_refund = \
            helper.calculateSoldTokensToSend(lovelace_received, self.minADAToSendWithToken, self.minFee, tokenPriceLovelace)
        self.assertEqual(tokens_to_send, 300000)
        self.assertEqual(lovelace_amount_to_refund, self.minADAToSendWithToken + 5)


    def test_calculate_insufficient_funds(self):
        lovelace_received = 1400000
        tokenPriceLovelace = 10
        tokens_to_send, lovelace_amount_to_refund = \
            helper.calculateSoldTokensToSend(lovelace_received, self.minADAToSendWithToken, self.minFee, tokenPriceLovelace)
        self.assertEqual(tokens_to_send, 0)
        self.assertEqual(lovelace_amount_to_refund, lovelace_received - self.minFee)
        

class TestCalculateEarnedTokensToSend(unittest.TestCase):
    minADAToSendWithToken = 1444443
    minFee = 200000
    stakingTokenRatio = 0.0000001
    def test_normal_case(self):
        tokens_to_send, lovelace_to_refund = \
            helper.calculateEarnedTokensToSend(2000000, self.minADAToSendWithToken, self.minFee, 10000000000, self.stakingTokenRatio)
        self.assertEqual(tokens_to_send, 1000)
        self.assertEqual(lovelace_to_refund, self.minADAToSendWithToken)


    def test_received_more(self):
        tokens_to_send, lovelace_to_refund = \
            helper.calculateEarnedTokensToSend(3000000, self.minADAToSendWithToken, self.minFee, 10000000000, self.stakingTokenRatio)
        self.assertEqual(tokens_to_send, 1000)
        self.assertEqual(lovelace_to_refund, self.minADAToSendWithToken)


    def test_exactly_the_fees(self):
        tokens_to_send, lovelace_to_refund = \
            helper.calculateEarnedTokensToSend(1444443+self.minFee, self.minADAToSendWithToken, self.minFee, 10000000000, self.stakingTokenRatio)
        self.assertEqual(tokens_to_send, 1000)
        self.assertEqual(lovelace_to_refund, self.minADAToSendWithToken)


    def test_less_than_the_fees(self):
        amount_received = self.minADAToSendWithToken + self.minFee - 1
        tokens_to_send, lovelace_to_refund = \
            helper.calculateEarnedTokensToSend(amount_received, self.minADAToSendWithToken, self.minFee, 10000000000, self.stakingTokenRatio)
        self.assertEqual(tokens_to_send, 0)
        self.assertEqual(lovelace_to_refund, amount_received - self.minFee)


def main() -> int:
    return 0

if __name__ == '__main__':
    print('Running some tests to verify validity of my helper functions.')
    blockFrostURL, blockFrostProjID = readConfigFile()
    unittest.main()