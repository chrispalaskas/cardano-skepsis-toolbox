import cardano_cli_helper as cli
import argparse
import glob
import os


def get_destination_addresses(destination_list, destination_folder):
    """Resolve destination addresses from either a list or a folder of .addr files."""
    addresses = []
    if destination_list:
        for item in destination_list:
            if os.path.exists(item):
                with open(item, 'r') as f:
                    addresses.append(f.read().strip())
            else:
                addresses.append(item.strip())
    elif destination_folder:
        assert os.path.isdir(destination_folder), \
            f"ERROR: Destination folder does not exist: {destination_folder}"
        addr_files = sorted(glob.glob(os.path.join(destination_folder, '*.addr')))
        assert len(addr_files) > 0, \
            f"ERROR: No .addr files found in {destination_folder}"
        for addr_file in addr_files:
            with open(addr_file, 'r') as f:
                addresses.append(f.read().strip())
            print(f"  Loaded address from {addr_file}")
    else:
        assert False, "ERROR: Provide either --destination-list or --destination-folder."
    return addresses


def verify_funds(wallet_tokens, num_destinations, lovelace_per_dest,
                 token_policy_id, token_amount_per_dest):
    """Verify the funding address has enough lovelace and tokens."""
    total_lovelace_needed = num_destinations * lovelace_per_dest
    total_tokens_needed = num_destinations * token_amount_per_dest

    available_lovelace = wallet_tokens.get('ADA', 0)
    available_tokens = wallet_tokens.get(token_policy_id, 0)

    print(f"\n--- Fund verification ---")
    print(f"  Destinations:        {num_destinations}")
    print(f"  Lovelace per dest:   {lovelace_per_dest}")
    print(f"  Tokens per dest:     {token_amount_per_dest}")
    print(f"  Total lovelace needed: {total_lovelace_needed} (+ fees)")
    print(f"  Total tokens needed:   {total_tokens_needed}")
    print(f"  Available lovelace:    {available_lovelace}")
    print(f"  Available tokens:      {available_tokens}")

    assert available_lovelace > total_lovelace_needed, \
        f"ERROR: Not enough lovelace. Have {available_lovelace}, " \
        f"need {total_lovelace_needed} + fees."
    assert available_tokens >= total_tokens_needed, \
        f"ERROR: Not enough tokens. Have {available_tokens}, " \
        f"need {total_tokens_needed}."
    print("  Funds OK.\n")


def build_multi_destination_tx(utxos, funding_addr, destinations,
                               lovelace_amount, token_policy_id,
                               token_amount, ttl, network, era):
    """Build a tx with 1 input set and N outputs."""
    print('Building multi-destination transaction...')
    command = f'cardano-cli {era} transaction build --{network} '
    for txIn in utxos:
        command += f'--tx-in {txIn} '

    # One --tx-out per destination
    for dest_addr in destinations:
        command += f'--tx-out {dest_addr}+{lovelace_amount}'
        command += f'+"{token_amount} {token_policy_id}" '

    command += f'--change-address {funding_addr} '
    command += f'--invalid-hereafter {ttl} '
    command += f'--out-file tx.raw'

    cli.getCardanoCliValue(command, '')[0]
    return cli.getTxId('tx.raw')


def main(funding_addr_input, funding_skey_file, destination_list,
         destination_folder, lovelace_amount, token_policy_id,
         token_amount, network, era):

    # Resolve funding address
    if os.path.exists(funding_addr_input):
        with open(funding_addr_input, 'r') as f:
            funding_addr = f.read().strip()
    else:
        funding_addr = funding_addr_input.strip()

    assert os.path.exists(funding_skey_file), \
        "ERROR: Funding skey file does not exist."

    # Resolve destinations
    destinations = get_destination_addresses(destination_list,
                                             destination_folder)
    print(f"Resolved {len(destinations)} destination addresses.")

    # Query UTxOs and wallet balance
    utxos_limit = 200
    utxos = cli.getAddrUTxOs(funding_addr, network, utxos_limit)
    wallet_tokens = cli.getTokenListFromTxHash(utxos)

    # Verify funds
    verify_funds(wallet_tokens, len(destinations), lovelace_amount,
                 token_policy_id, token_amount)

    # Build transaction
    ttl = cli.queryTip('slot', network) + 1000
    tx_id = build_multi_destination_tx(
        utxos, funding_addr, destinations,
        lovelace_amount, token_policy_id, token_amount,
        ttl, network, era
    )
    tx_id = tx_id.strip()
    print(f"Transaction ID: {tx_id}")

    # Sign
    cli.signTx([funding_skey_file], network=network)

    # Submit
    submitted = cli.submitSignedTx(network=network)
    assert 'Transaction successfully submitted' in submitted, \
        f"ERROR: Transaction not submitted successfully. Message: {submitted}"
    print("Done.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Send tokens to multiple destinations in a single transaction.'
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
        '-a', '--funding-addr',
        required=True,
        dest='funding_addr',
        metavar='ADDR',
        help='Funding address or path to .addr file.',
        type=str
    )
    parser.add_argument(
        '-k', '--funding-skey-file',
        required=True,
        dest='funding_skey_file',
        metavar='SKEY',
        help='Path to funding signing key file.',
        type=str
    )
    parser.add_argument(
        '-d', '--destination-list',
        default=None,
        dest='destination_list',
        metavar='ADDR',
        nargs='+',
        help='List of destination addresses or .addr files.',
        type=str
    )
    parser.add_argument(
        '-f', '--destination-folder',
        default=None,
        dest='destination_folder',
        metavar='FOLDER',
        help='Folder to scan for *.addr files as destinations.',
        type=str
    )
    parser.add_argument(
        '-l', '--amount-lovelace',
        default=1*10**6,
        dest='lovelace_amount',
        metavar='LOVELACE',
        help='Amount of lovelace to send to each destination.',
        type=int
    )
    parser.add_argument(
        '-t', '--token-policy-id',
        required=True,
        dest='token_policy_id',
        metavar='POLICY_ID',
        help='Token policy ID (format: policyId.tokenName).',
        type=str
    )
    parser.add_argument(
        '-m', '--token-amount',
        required=True,
        dest='token_amount',
        metavar='AMOUNT',
        help='Number of tokens to send to each destination.',
        type=int
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

    main(args.funding_addr,
         args.funding_skey_file,
         args.destination_list,
         args.destination_folder,
         args.lovelace_amount,
         args.token_policy_id,
         args.token_amount,
         args.network,
         args.era)
