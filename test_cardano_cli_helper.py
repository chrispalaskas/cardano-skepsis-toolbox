import unittest
import cardano_cli_helper as cli


class TestCardanoCliHelper(unittest.TestCase):
    utxosJson = {
        '9d9dc0fcc51f0646fbf5742c02f004d266dc7badac259f71b36e23774cc5d1e1#1': {
            'address': 'addr1v86pqugsjsu3enxnxxl9ky8g6eefvddtzvyted4mv0pwuysfj0zhz',
            'value': {
                '8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce': {'536b65707369734e4654': 30},
                'lovelace': 11563189
            }
        },
        'ANOTHER_TXHASH_ADDRESS#0': {
            'address': 'addrxxxxxxxxxxxxxxxxxxxxxxxxxx0pwuysfj0zhz',
            'value': {
                '8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce': {'536b65707369734e4654': 50},
                'lovelace': 11563189000
            }
        },
        'YET_ANOTHER_TXHASH_ADDRESS#0': {
            'address': 'addryyyyyyyyyyyyyyyyyy',
            'value': {
                '8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce': {'536b65707369734e4654': 100},
                'lovelace': 11563189000000
            }
        },
    }

    utxosJsonWithForeignToken = {
        "0c5f94f89d9de26c0fbb0f5a64a1e75ef0c02460a676c56d45279d66ab590aea#0": {
            "address": "addr1v86pqugsjsu3enxnxxl9ky8g6eefvddtzvyted4mv0pwuysfj0zhz",
            "value": {
                "lovelace": 1444443,
                "860b987103e7ad9b90657097b8744951fdf8eaa007b11c78528f75cc": {
                    "41534b50": 1000
                }
            }
        },
        "bd43b272660078011226f8bb3c3cc80ff8d3f10c59024692ebf87f926458b44e#0": {
            "address": "addr1v86pqugsjsu3enxnxxl9ky8g6eefvddtzvyted4mv0pwuysfj0zhz",
            "value": {
                "lovelace": 999980
            }
        },
        "bd43b272660078011226f8bb3c3cc80ff8d3f10c59024692ebf87f926458b44e#1": {
            "address": "addr1v86pqugsjsu3enxnxxl9ky8g6eefvddtzvyted4mv0pwuysfj0zhz",
            "value": {
                "8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce": {
                    "536b65707369734e4654": 30
                },
                "860b987103e7ad9b90657097b8744951fdf8eaa007b11c78528f75cc": {
                    "41534b50": 1000
                },
                "lovelace": 10033618
            }
        }
    }

    def test_getTokenListFromTxHash(self):
        expected_tokensDict = {'8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce.536b65707369734e4654': 180,
                               'ADA': 11574763752189}
        tokensDict = cli.getTokenListFromTxHash(self.utxosJson)
        self.assertDictEqual(expected_tokensDict, tokensDict)

    def test_getTxInWithLargestTokenAmount(self):
        tokenPolicyID = '8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce.536b65707369734e4654'

        maxTokenTxHash = cli.getTxInWithLargestTokenAmount(self.utxosJson, tokenPolicyID)
        self.assertEqual(maxTokenTxHash, 'YET_ANOTHER_TXHASH_ADDRESS#0')

    def test_getTokenListFromTxHash_w_foreign(self):
        expected_tokensDict = {'8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce.536b65707369734e4654': 30,
                               '860b987103e7ad9b90657097b8744951fdf8eaa007b11c78528f75cc.41534b50': 2000,
                               'ADA': 12478041}
        tokensDict = cli.getTokenListFromTxHash(self.utxosJsonWithForeignToken)
        self.assertDictEqual(expected_tokensDict, tokensDict)

    def test_getTxInWithLargestTokenAmount_w_foreign(self):
        tokenPolicyID = '8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce.536b65707369734e4654'

        maxTokenTxHash = cli.getTxInWithLargestTokenAmount(self.utxosJsonWithForeignToken, tokenPolicyID)
        self.assertEqual(maxTokenTxHash, 'bd43b272660078011226f8bb3c3cc80ff8d3f10c59024692ebf87f926458b44e#1')

    def test_getForeignTokensFromTokenList(self):
        tokensDict = {
            '8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce.536b65707369734e4654': 30,
            '860b987103e7ad9b90657097b8744951fdf8eaa007b11c78528f75cc.41534b50': 1000,
            'ADA': 12478041
        }
        tokensDictOld = {
            '8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce.536b65707369734e4654': 30,
            '860b987103e7ad9b90657097b8744951fdf8eaa007b11c78528f75cc.41534b50': 1000,
            'ADA': 12478041
        } # Verify that the initial dictionary doesn't change
        foreignTokensDict = cli.getForeignTokensFromTokenList(tokensDict, '8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce.536b65707369734e4654')
        self.assertDictEqual(foreignTokensDict, {'860b987103e7ad9b90657097b8744951fdf8eaa007b11c78528f75cc.41534b50': 1000})
        self.assertDictEqual(tokensDictOld, tokensDict)

def main() -> int:
    return 0

if __name__ == '__main__':
    print('Running some tests to verify validity of my cardano-cli-helper functions.')
    unittest.main()