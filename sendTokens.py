import cardano_cli_helper as cli
import argparse
from os.path import exists


def main(paymentAddrFile, paymentSkeyFile, recipientAddr, lovelace_amount,
         policyIDList, tokenAmountList, network, era):
    if exists(paymentAddrFile):
        with open(paymentAddrFile, 'r') as file:
            paymentAddr = file.read().strip()
    else:
        paymentAddr = paymentAddrFile.strip()

    assert exists(paymentSkeyFile), "ERROR: Payment skey file does not exist."
    assert len(policyIDList) == len(tokenAmountList), \
        "ERROR: Policy ID list does not match with Token amount List."

    if exists(recipientAddr):
        # If it doesn't exist assume it's a valid address
        with open(recipientAddr, 'r') as file:
            recipientAddr = file.read().strip()
    # Create dictionary with tokens to send
    sendTokensDict = {}
    for tokenID, tokenAmount in zip(policyIDList, tokenAmountList):
        sendTokensDict[tokenID] = tokenAmount

    utxos = cli.getAddrUTxOs(paymentAddr, network)
    dictWallet = cli.getTokenListFromTxHash(utxos)

    try:
        for item in sendTokensDict:
            dictWallet[item] = dictWallet[item] - sendTokensDict[item]
    except Exception as e:
        assert False, f"ERROR: Token amounts not found in wallet: {e}"

    ttlSlot = cli.queryTip('slot', network) + 1000

    txId = cli.buildSendTokensToOneDestinationTx(
        utxos, paymentAddr, ttlSlot,
        recipientAddr, lovelace_amount,
        sendTokensDict, dictWallet,
        network, era=era
    )
    txId = txId.strip()
    cli.signTx([paymentSkeyFile], network=network)
    submitted = cli.submitSignedTx(network=network)
    assert (
        submitted.strip() == 'Transaction successfully submitted.'
    ), f"ERROR: Transaction {txId} not submitted successfully"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--payment-addr',
                    default='/opt/cardano/cnode/priv/wallet/SkepsisCoinWallet/payment.addr',
                    dest='payment_addr',
                    help='Provide payment address or location of payment address file.',
                    type=str
                    )
    parser.add_argument('-K', '--payment-skey-file',
                    default='/opt/cardano/cnode/priv/wallet/SkepsisCoinWallet/payment.skey',
                    dest='payment_skey_file',
                    help='Provide location of payment skey file.',
                    type=str
                    )
    parser.add_argument('-D', '--destination',
                    default='/home/christos/skepsis_withdraw/myYoroi.addr',
                    dest='destination',
                    help='Provide location destination address file or string.',
                    type=str
                    )
    parser.add_argument('-L', '--amount-lovelace',
                    default=int(0*10**6),
                    dest='amount',
                    help='Provide amount to send in lovelace.',
                    type=int
                    )
    parser.add_argument('-T','--token-policy-id',
                    default=[],
                    dest='policyIDList',
                    nargs='+',
                    help='List of tokens to send',
                    type=str)
    parser.add_argument('-M','--token-amount',
                    default=[],
                    dest='tokenAmountList',
                    nargs='+',
                    help='List of tokens to send',
                    type=int)
    parser.add_argument('-N', '--network',
                    default='mainnet',
                    dest='network',
                    help='Provide cardano network.',
                    type=str
                    )
    parser.add_argument('-E', '--era',
                    default='babbage-era',
                    dest='era',
                    help='Provide cardano era.',
                    type=str
                    )
    args = parser.parse_args()

    main(args.payment_addr,
         args.payment_skey_file,
         args.destination,
         args.amount,
         args.policyIDList,
         args.tokenAmountList,
         args.network,
         args.era)
