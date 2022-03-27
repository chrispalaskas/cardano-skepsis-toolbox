import cardano_cli_helper as cli
from os.path import exists
import urllib.request


def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False


def main():
    sign = False
    if sign:
        if connect():
            print('Please go offline before proceeding to access cold keys.')
            return 0
        if not exists('/media/christos/TOSHIBA/kryakleis'):
            print('Please insert USB stick with keys')
            return 0
        cli.getProtocolJson()
        myPaymentAddrFile = '/home/christos/skepsis_withdraw/payment.addr'
        myPaymentSkeyFile = '/home/christos/skepsis_withdraw/payment.skey'
        myStakeAddrFile = '/home/christos/skepsis_withdraw/stake.addr'
        with open(myPaymentAddrFile) as file:
            paymentAddr = file.read()
        with open(myStakeAddrFile) as file:
            stakeAddr = file.read()
        lovelace, utxos = cli.getLovelaceBalance(paymentAddr)
        utxo = utxos[0]
        stake_rewards = cli.getStakeBalance(stakeAddr)
        cli.getRawTxStakeWithdraw(utxo, paymentAddr, stakeAddr)
        minFee = cli.getMinFee(1, 0)

        withdrawal = lovelace - minFee + stake_rewards
        cli.buildRawTxStakeWithdraw(utxo, paymentAddr, withdrawal, stakeAddr, stake_rewards, minFee)
        cli.signTxStakeWithdraw(myPaymentSkeyFile)
    else:
        if exists('/media/christos/TOSHIBA/kryakleis'):
            print('Please remove USB stick with keys, before you go online.')
            return 0
        if not connect():
            print('Please go online to submit transaction.')
            return 0
        cli.submitSignedTx('withdraw_rewards.signed')
    



if __name__ == '__main__':
    main()