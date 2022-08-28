import cardano_cli_helper as cli
from os.path import exists
import urllib.request
import argparse


def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False


def main(payment_addr_file, payment_skey_file, stake_addr_file, stake_skey_file, is_online=False):
    if not is_online:
        if connect():
            print('Please go offline before proceeding to access cold keys.')
            return 0
        if not exists(stake_skey_file):
            print('Please insert USB stick with keys')
            return 0
        cli.getProtocolJson()

        with open(payment_addr_file) as file:
            paymentAddr = file.read()
        with open(stake_addr_file) as file:
            stakeAddr = file.read()
        utxos = cli.getAddrUTxOs(paymentAddr)
        utxo = list(utxos.keys())[0]
        lovelace = utxos[utxo]['value']['lovelace']

        stake_rewards = cli.getStakeBalance(stakeAddr)
        cli.getRawTxStakeWithdraw(utxo, paymentAddr, stakeAddr)
        minFee = cli.getMinFee(1, 1)

        withdrawal = lovelace - minFee + stake_rewards

        cli.buildRawTxStakeWithdraw(utxo, paymentAddr, withdrawal, stakeAddr, stake_rewards, minFee)
        cli.signTx([payment_skey_file, stake_skey_file], filename='withdraw_rewards')
    else:
        if exists(stake_skey_file):
            print('Please remove USB stick with keys, before you go online.')
            return 0
        if not connect():
            print('Please go online to submit transaction.')
            return 0
        cli.submitSignedTx('withdraw_rewards')




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-A', '--payment-addr-file',
                    default='/home/christos/skepsis_withdraw/payment.addr',
                    dest='payment_addr_file',
                    help='Provide location of payment address file.',
                    type=str
                    )
    parser.add_argument('-K', '--payment-skey-file',
                    default='/home/christos/skepsis_withdraw/payment.skey',
                    dest='payment_skey_file',
                    help='Provide location of payment skey file.',
                    type=str
                    )
    parser.add_argument('-P', '--stake-addr-file',
                    default='/home/christos/skepsis_withdraw/stake.addr',
                    dest='stake_addr_file',
                    help='Provide location of stake address file.',
                    type=str
                    )
    parser.add_argument('-S', '--stake-skey-file',
                    default='/media/christos/TOSHIBA/kryakleis/stake.skey',
                    dest='stake_skey_file',
                    help='Provide location stake skey file.',
                    type=str
                    )
    parser.add_argument('--sign', dest='online', action='store_false')
    parser.add_argument('--submit', dest='online', action='store_true')
    # Step 1: Offline, set to False, sign with usb stick.
    # Step 2: Online, set to True, submit
    parser.set_defaults(online=False)
    args = parser.parse_args()
    main(args.payment_addr_file,
         args.payment_skey_file,
         args.stake_addr_file,
         args.stake_skey_file,
         args.online)
