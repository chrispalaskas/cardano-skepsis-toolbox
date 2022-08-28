import unittest
import json
import send_assets_to_recipients as sendAssets
import cardano_cli_helper as cli
import helper


class TestGetStakeFromAddress(unittest.TestCase):

    def test_get_stake_from_address(self):
        tokenRecipientList = [cli.Recipient('addr1qx5trqazps96kt7539ye9cs65nu7kww0ttlgk7u8g3eadrkaphzwpa6dwpquhtgumlqqmzxl8fqr9whzqyx394erpptqq4rdxh',
                                            'stake1u8wsm38q7axhqswt45wdlsqd3r0n5spjht3qzrgj6u3ss4slthexn',
                                            2000000,
                                            1444443,
                                            [tokenPolicyID],
                                            [200])]

        if sendAssets.main( tokenRecipientList,
                            myPaymentAddrFile,
                            myPaymentAddrSignKeyFile,
                            sentTokensLogFile,
                            delegatorsLogFile,
                            minFee):
            print('Success!')
        else:
            print('Failure')

def main() -> int:
    return 0

if __name__ == '__main__':
    print('Running some tests to verify validity of my helper functions.')
    myPaymentAddrFile, \
    myPaymentAddrSignKeyFile, \
    tokenPolicyID, \
    sentTokensLogFile, \
    delegatorsLogFile, \
    minFee, \
    finRecipientObjList  = helper.parseConfigSendAssets('./config.json',[],[])
    unittest.main()