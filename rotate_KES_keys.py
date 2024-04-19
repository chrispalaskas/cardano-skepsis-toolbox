import cardano_cli_helper as cli
import urllib.request
import argparse

NETWORK = 'mainnet'


def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)  # Python 3.x
        return True
    except Exception as e:
        print(f"ERROR: Could not connect to the internet: {e}")
        return False


def main(kes_vkey_file,
         cold_skey_file,
         cold_counter_file):
    if connect():
        print('Please go offline before proceeding to generate KES keys.')
        return 0
    cli.generateKESkeys()
    slotsPerKESPeriod = cli.getSlotsPerKESPeriod()
    assert slotsPerKESPeriod > 0, 'slotsPerKESPeriod is zero'

    # Use the kes.vkey that was just generated
    if not cli.generateOperationalCertificate(
        kes_vkey_file,
        cold_skey_file,
        cold_counter_file,
        slotsPerKESPeriod,
        NETWORK
    ):
        print('ERROR: Certificate not generated.')
    else:
        print('Certificate generated.')
    # Replace kes.skey and node.cert at your block producer
    # Store kes.skey, kes.vkey and node.cert on usb stick
    # Note that the kes.counter will be updated on your usb stick


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-V', '--kes-vkey-file',
        default='kes.vkey',
        dest='kes_vkey_file',
        help='Provide location of kes vkey file.',
        type=str
    )
    parser.add_argument(
        '-C', '--cold-skey-file',
        default='/media/christos/TOSHIBA/kryakleis/cold.skey',
        dest='cold_skey_file',
        help='Provide location of cold skey file.',
        type=str
    )
    parser.add_argument(
        '-R', '--cold-counter-file',
        default='/media/christos/TOSHIBA/kryakleis/cold.counter',
        dest='cold_counter_file',
        help='Provide location of cold counter file.',
        type=str
    )

    args = parser.parse_args()
    main(args.kes_vkey_file,
         args.cold_skey_file,
         args.cold_counter_file)
