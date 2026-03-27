import cardano_cli_helper as cli
import argparse
import glob
import os


def get_source_accounts(source_list, source_folder):
    """Resolve source accounts as list of (addr, skey_file) tuples.

    Each source needs both an address and a signing key.
    - source_list: list of .addr file paths (matching .skey expected alongside)
    - source_folder: folder to scan for *.addr files (matching .skey expected)
    """
    accounts = []
    if source_list:
        for item in source_list:
            if os.path.exists(item) and item.endswith('.addr'):
                skey_file = item.replace('.addr', '.skey')
                assert os.path.exists(skey_file), \
                    f"ERROR: Matching skey not found for {item} (expected {skey_file})"
                with open(item, 'r') as f:
                    addr = f.read().strip()
                accounts.append((addr, skey_file))
            else:
                assert False, \
                    f"ERROR: Source list items must be .addr file paths. Got: {item}"
    elif source_folder:
        assert os.path.isdir(source_folder), \
            f"ERROR: Source folder does not exist: {source_folder}"
        addr_files = sorted(glob.glob(os.path.join(source_folder, '*.addr')))
        assert len(addr_files) > 0, \
            f"ERROR: No .addr files found in {source_folder}"
        for addr_file in addr_files:
            skey_file = addr_file.replace('.addr', '.skey')
            assert os.path.exists(skey_file), \
                f"ERROR: Matching skey not found for {addr_file} (expected {skey_file})"
            with open(addr_file, 'r') as f:
                addr = f.read().strip()
            accounts.append((addr, skey_file))
            print(f"  Loaded account from {addr_file}")
    else:
        assert False, "ERROR: Provide either --source-list or --source-folder."
    return accounts


def sweep_address(source_addr, source_skey, destination_addr, network, era):
    """Send all funds (lovelace + tokens) from source to destination."""
    utxos = cli.getAddrUTxOs(source_addr, network)
    if len(utxos) == 0:
        print(f"  Skipping {source_addr[:20]}... — no UTxOs found.")
        return None

    wallet_tokens = cli.getTokenListFromTxHash(utxos)
    print(f"  Balance: {wallet_tokens}")

    ttl = cli.queryTip('slot', network) + 1000

    # Build tx: all UTxOs as inputs, change-address = destination
    # This sweeps everything (ADA + all tokens) to the destination.
    command = f'cardano-cli {era} transaction build --{network} '
    for txIn in utxos:
        command += f'--tx-in {txIn} '
    command += f'--change-address {destination_addr} '
    command += f'--invalid-hereafter {ttl} '
    command += f'--out-file tx.raw'

    cli.getCardanoCliValue(command, '')[0]
    tx_id = cli.getTxId('tx.raw').strip()

    cli.signTx([source_skey], network=network)
    submitted = cli.submitSignedTx(network=network)
    assert 'Transaction successfully submitted' in submitted, \
        f"ERROR: Transaction not submitted. Message: {submitted}"

    return tx_id


def main(source_list, source_folder, destination_input, network, era):
    # Resolve destination address
    if os.path.exists(destination_input):
        with open(destination_input, 'r') as f:
            destination_addr = f.read().strip()
    else:
        destination_addr = destination_input.strip()

    # Resolve source accounts
    accounts = get_source_accounts(source_list, source_folder)
    print(f"Found {len(accounts)} source accounts.")
    print(f"Destination: {destination_addr[:20]}...\n")

    results = []
    for i, (addr, skey) in enumerate(accounts):
        print(f"--- Sweeping account {i+1}/{len(accounts)} ---")
        print(f"  Address: {addr[:20]}...")
        tx_id = sweep_address(addr, skey, destination_addr, network, era)
        if tx_id:
            print(f"  Tx submitted: {tx_id}")
            results.append((addr, tx_id))
        print()

    print(f"=== Summary: {len(results)}/{len(accounts)} addresses swept ===")
    for addr, tx_id in results:
        print(f"  {addr[:20]}... -> {tx_id}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Sweep all funds from multiple source addresses to one destination.'
    )
    parser.add_argument(
        '-n', '--network',
        default='mainnet',
        dest='network',
        metavar='NETWORK',
        help='Provide cardano network (e.g. mainnet, testnet-magic 9).',
        type=str
    )
    parser.add_argument(
        '-s', '--source-list',
        default=None,
        dest='source_list',
        metavar='ADDR',
        nargs='+',
        help='List of .addr file paths (matching .skey files expected alongside).',
        type=str
    )
    parser.add_argument(
        '-f', '--source-folder',
        default=None,
        dest='source_folder',
        metavar='FOLDER',
        help='Folder to scan for *.addr files (matching .skey files expected).',
        type=str
    )
    parser.add_argument(
        '-d', '--destination',
        required=True,
        dest='destination',
        metavar='ADDR',
        help='Destination address or path to .addr file.',
        type=str
    )
    parser.add_argument(
        '-e', '--era',
        default='conway',
        dest='era',
        metavar='ERA',
        help='Cardano era.',
        type=str
    )
    args = parser.parse_args()

    main(args.source_list,
         args.source_folder,
         args.destination,
         args.network,
         args.era)
