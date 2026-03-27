import argparse
import generateAddr


def main(network, start, end):
    for i in range(start, end + 1):
        name = f'payment_{i}'
        print(f'--- Generating {name} ---')
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
