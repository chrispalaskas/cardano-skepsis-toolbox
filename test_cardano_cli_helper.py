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

    def test_getTokenListFromTxHash(self):
        expected_tokensDict = {'8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce.536b65707369734e4654': 180,
                               'ADA': 11574763752189}
        tokensDict = cli.getTokenListFromTxHash(self.utxosJson)
        self.assertDictEqual(expected_tokensDict, tokensDict)

    def test_getTxInWithLargestTokenAmount(self):
        tokenPolicyID = '8b0720a40d2c7bb6b7f3ee9bf200c60363c3baa0df787260f58cf7ce.536b65707369734e4654'
        
        maxTokenTxHash = cli.getTxInWithLargestTokenAmount(self.utxosJson, tokenPolicyID)
        self.assertEqual(maxTokenTxHash, 'YET_ANOTHER_TXHASH_ADDRESS#0')


def main() -> int:
    return 0

if __name__ == '__main__':
    print('Running some tests to verify validity of my cardano-cli-helper functions.')
    unittest.main()