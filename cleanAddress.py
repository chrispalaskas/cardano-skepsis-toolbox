import cardano_cli_helper as cli
import argparse
from os.path import exists
import copy  # For dictionary deepcopy


def main(paymentAddrFile, paymentSkeyFile, garbageAddrFile,
         policyIDToKeepList, network, era):
    if exists(paymentAddrFile):
        with open(paymentAddrFile, 'r') as file:
            paymentAddr = file.read().strip()
    else:
        paymentAddr = paymentAddrFile.strip()

    assert exists(paymentSkeyFile), "ERROR: Payment skey file does not exist."

    if exists(garbageAddrFile):
        with open(garbageAddrFile, 'r') as file:
            garbageAddr = file.read().strip()
    else:
        garbageAddr = garbageAddrFile.strip()

    utxo_limit = 200 # Ensures that the tx can fit in a block
    # TODO: The number should be better calculated in bytes though
    utxos = cli.getAddrUTxOs(paymentAddr, network, utxo_limit)
    dictWallet = cli.getTokenListFromTxHash(utxos)
    ttlSlot = cli.queryTip('slot', network) + 1000

    destinationDict = copy.deepcopy(dictWallet)
    destinationDict.pop("ADA", None)
    returnDict = {"ADA": dictWallet["ADA"]}
    for policy in policyIDToKeepList:
        if policy in dictWallet.keys():
            destinationDict.pop(policy, None)
            returnDict[policy] = dictWallet[policy]

    cli.buildSendTokensToOneDestinationTx(
        utxos, paymentAddr, ttlSlot, garbageAddr,
        0, destinationDict, returnDict, network, era=era
        )
    cli.signTx([paymentSkeyFile], network=network)

    print(cli.submitSignedTx(network=network))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-A', '--payment-addr',
        default='account1.addr',
        dest='payment_addr',
        help='Provide payment address or location of payment address file.',
        type=str
        )
    parser.add_argument(
        '-K', '--payment-skey-file',
        default='account1.skey',
        dest='payment_skey_file',
        help='Provide location of payment skey file.',
        type=str
        )
    parser.add_argument(
        '-D', '--destination',
        default='garbage.addr',
        dest='destination',
        help='Provide location destination address file or string.',
        type=str
        )
    parser.add_argument(
        '-T', '--keep-token-policy-id',
        default=[],
        dest='keepPolicyIDList',
        nargs='+',
        help='List of tokens to send',
        type=str)
    parser.add_argument(
        '-N', '--network',
        default='testnet-magic 2',
        dest='network',
        help='Provide cardano network.',
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

    main(args.payment_addr,
         args.payment_skey_file,
         args.destination,
         args.keepPolicyIDList,
         args.network,
         args.era)
