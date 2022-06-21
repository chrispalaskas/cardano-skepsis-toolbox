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


def main():
    if connect():
        print('Please go offline before proceeding to generate KES keys.')
        return 0
    cli.generateKESkeys()
    slotesPerKESPeriod = cli.getSlotsPerKESPeriod()
    currentTip = cli.getCurrentSlot()
    currentKESPeriod = int(currentTip / slotesPerKESPeriod)
    if not cli.generateOperationalCertificate(
        'kes.vkey',
        '/media/christos/TOSHIBA/kryakleis/cold.skey',
        '/media/christos/TOSHIBA/kryakleis/cold.counter',
        currentKESPeriod):
        print('ERROR: Certificate not generated.')
    else:
        print('Certificate generated.')


if __name__ == '__main__':
    main()
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-A', '--payment-addr-file',
    #                 default='/home/christos/skepsis_withdraw/payment.addr',
    #                 dest='payment_addr_file',
    #                 help='Provide location of payment address file.',
    #                 type=str
    #                 )
    # parser.add_argument('-K', '--payment-skey-file',
    #                 default='/home/christos/skepsis_withdraw/payment.skey',
    #                 dest='payment_skey_file',
    #                 help='Provide location of payment skey file.',
    #                 type=str
    #                 )
    # parser.add_argument('-P', '--stake-addr-file',
    #                 default='/home/christos/skepsis_withdraw/stake.addr',
    #                 dest='stake_addr_file',
    #                 help='Provide location of stake address file.',
    #                 type=str
    #                 )
    # parser.add_argument('-S', '--stake-skey-file',
    #                 default='/media/christos/TOSHIBA/kryakleis/stake.skey',
    #                 dest='stake_skey_file',
    #                 help='Provide location stake skey file.',
    #                 type=str
    #                 )
    # parser.add_argument('--sign', dest='online', action='store_false')
    # parser.add_argument('--submit', dest='online', action='store_true')
    # parser.set_defaults(online=False)
    # args = parser.parse_args()
    # main(args.payment_addr_file,
    #      args.payment_skey_file,
    #      args.stake_addr_file,
    #      args.stake_skey_file,
    #      args.online)