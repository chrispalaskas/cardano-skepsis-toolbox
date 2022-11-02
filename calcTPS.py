import cardano_cli_helper as cli
import argparse
from os.path import exists

# Let x be the number of outputs you can fit in a transaction of 16kB (on mainnet).
# Then you can fit y transactions into one block (currently 5.5  .. so 5 given mainnet params)
# We can produce a block at most every 1/f slots (currently that is 0.05 and slots are 1 second right now .. so every 20 seconds).
# Best case transactions-per-second would be (x * y) / (1 / f) = (x * y) * f = x * 5 * 0.05 = x * 0.25

MaxTxSizeUTxO = 16*1024
TXS_PER_BLOCK = 5
PARAMETER_f = 0.05
ERA = 'babbage-era'
NETWORK = 'testnet-magic 9'
TOTAL_TXOUT = 414
LOVELACE_AMOUNT = 900000

def main(paymentAddrFile, paymentSkeyFile, destinationFile):

    print('Building raw Tx for max outputs')
    if exists(paymentAddrFile):
        with open(paymentAddrFile, 'r') as file:
            paymentAddr = file.read().strip()
    else:
        paymentAddr = paymentAddrFile.strip()
    if exists(destinationFile):
        with open(destinationFile, 'r') as file:
            destination = file.read().strip()
    else:
        destination = destinationFile.strip()
    if not exists(paymentSkeyFile):
        print('ERROR: Payment skey file does not exist.')
        return 0
    utxos = cli.getAddrUTxOs(paymentAddr, NETWORK)
    maxLovelace = 0
    for utxo in utxos:
        if int(utxos[utxo]['value']['lovelace']) > maxLovelace:
            maxLovelace = int(utxos[utxo]['value']['lovelace'])
            txIn = utxo
    ttlSlot = cli.queryTip('slot', NETWORK) + 1000
    command = f'cardano-cli transaction build \
                --{ERA} '
    command += f'--tx-in {txIn} '
    for x in range(TOTAL_TXOUT):
        command += f'--tx-out {destination}+{LOVELACE_AMOUNT} '
    command += f' --change-address {paymentAddr} \
                --{NETWORK}  \
                --out-file tx.raw \
                --invalid-hereafter {ttlSlot}'
    cli.getCardanoCliValue(command, '')

    cli.signTx([paymentSkeyFile],network=NETWORK)

    res = cli.submitSignedTx(network=NETWORK)

    if res.strip() == 'Transaction successfully submitted.':
        TPS = TXS_PER_BLOCK * TOTAL_TXOUT / (1 / PARAMETER_f)
        print('Max TPS:', TPS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--payment-addr',
                    default='/home/christos/IOHK/repos/cardano-skepsis-toolbox/maxTPS.addr',
                    dest='payment_addr',
                    help='Provide payment address or location of payment address file.',
                    type=str
                    )
    parser.add_argument('-K', '--payment-skey-file',
                    default='/home/christos/IOHK/repos/cardano-skepsis-toolbox/maxTPS.skey',
                    dest='payment_skey_file',
                    help='Provide location of payment skey file.',
                    type=str
                    )
    parser.add_argument('-D', '--destination',
                    default = '/home/christos/IOHK/repos/cardano-skepsis-toolbox/maxedOUT.addr',
                    dest='destination',
                    help='Provide location destination address file or string.',
                    type=str
                    )
    args = parser.parse_args()

    main(args.payment_addr,
         args.payment_skey_file,
         args.destination,)