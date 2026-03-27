import argparse
import os
import cardano_cli_helper as cli


def main(network, start, end, output_folder, with_staking=False):
    os.makedirs(output_folder, exist_ok=True)
    for i in range(start, end + 1):
        name = os.path.join(output_folder, f'payment_{i}')
        stake_name = os.path.join(output_folder, f'stake_{i}')
        print(f'--- Generating payment_{i} ---')
        cli.generatePaymentKeyPair(name)
        if with_staking:
            cli.generateStakeKeyPair(stake_name)
            cli.generatePaymentAddressForStaking(network, name,
                                                 f'{stake_name}.vkey')
            print(f'Created {name}.addr/skey/vkey, {stake_name}.skey/vkey')
        else:
            cli.generatePaymentAddress(network, name)
            print(f'Created {name}.addr, {name}.skey, {name}.vkey')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate multiple payment addresses.')
    parser.add_argument(
        '-n', '--network',
        default='mainnet',
        metavar='NETWORK',
        help='Provide cardano network.',
        type=str
    )
    parser.add_argument(
        '-s', '--start',
        required=True,
        metavar='START',
        help='Start index (inclusive).',
        type=int
    )
    parser.add_argument(
        '-e', '--end',
        required=True,
        metavar='END',
        help='End index (inclusive).',
        type=int
    )
    parser.add_argument(
        '-o', '--output-folder',
        default='generated_addresses',
        dest='output_folder',
        metavar='FOLDER',
        help='Output folder for generated address files.',
        type=str
    )
    parser.add_argument(
        '--with-staking-key',
        default=False,
        dest='with_staking',
        action='store_true',
        help='Also generate a stake key pair per address.',
    )
    args = parser.parse_args()
    main(args.network, args.start, args.end, args.output_folder,
         args.with_staking)
