import argparse
import os
import generateAddr


def main(network, start, end, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for i in range(start, end + 1):
        name = os.path.join(output_folder, f'payment_{i}')
        print(f'--- Generating payment_{i} ---')
        generateAddr.generateAccount(network, name)
        print(f'Created {name}.addr, {name}.skey, {name}.vkey')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate multiple payment addresses.')
    parser.add_argument(
        '-n', '--network',
        default='mainnet',
        help='Provide cardano network.',
        type=str
    )
    parser.add_argument(
        '-s', '--start',
        required=True,
        help='Start index (inclusive).',
        type=int
    )
    parser.add_argument(
        '-e', '--end',
        required=True,
        help='End index (inclusive).',
        type=int
    )
    parser.add_argument(
        '-o', '--output-folder',
        default='generated_addresses',
        dest='output_folder',
        help='Output folder for generated address files.',
        type=str
    )
    args = parser.parse_args()
    main(args.network, args.start, args.end, args.output_folder)
