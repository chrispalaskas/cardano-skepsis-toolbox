import argparse
import os
import generateAddr


def main(network, start, end):
    os.makedirs('generated_addresses', exist_ok=True)
    for i in range(start, end + 1):
        name = os.path.join('generated_addresses', f'payment_{i}')
        print(f'--- Generating payment_{i} ---')
        generateAddr.generateAccount(network, name)
        print(f'Created {name}.addr, {name}.skey, {name}.vkey')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate multiple payment addresses.')
    parser.add_argument(
        '-N', '--network',
        default='mainnet',
        help='Provide cardano network.',
        type=str
    )
    parser.add_argument(
        '-S', '--start',
        required=True,
        help='Start index (inclusive).',
        type=int
    )
    parser.add_argument(
        '-E', '--end',
        required=True,
        help='End index (inclusive).',
        type=int
    )
    args = parser.parse_args()
    main(args.network, args.start, args.end)
