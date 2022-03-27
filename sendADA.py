import cardano_cli_helper as cli


def main(paymentAddr, myPaymentSkeyFile, recipientAddr, lovelace_amount):
    lovelace, utxos = cli.getLovelaceBalance(paymentAddr)
    ttlSlot = cli.getCurrentSlot() + 1000    
    cli.getDraftTXSimple(utxos, paymentAddr, recipientAddr, ttlSlot)
    minFee = cli.getMinFee(len(utxos),1)
    lovelace_return = lovelace - minFee - lovelace_amount
    cli.getRawTxSimple(utxos,paymentAddr,recipientAddr, lovelace_amount, lovelace_return, ttlSlot, minFee)
    cli.signTx(myPaymentSkeyFile)
    cli.submitSignedTx()

if __name__ == '__main__':
    myPaymentAddrFile = '/home/christos/skepsis_withdraw/payment.addr'
    myPaymentSkeyFile = '/home/christos/skepsis_withdraw/payment.skey'
    myYoroiAddrFile = '/home/christos/skepsis_withdraw/myYoroi.addr'
    with open(myPaymentAddrFile) as file:
        paymentAddr = file.read()
    with open(myYoroiAddrFile) as file:
        recipientAddr = file.read()
    main(paymentAddr, myPaymentSkeyFile, recipientAddr, 1400000000)