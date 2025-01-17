import json
import os
import sys

from loguru import logger

try:
    from solana.keypair import Keypair
    from solana.publickey import PublicKey
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts
    from solana.system_program import SYS_PROGRAM_ID
    from solana.transaction import Transaction
except ImportError:
    import subprocess

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "solana"]
    )
    from solana.keypair import Keypair
    from solana.publickey import PublicKey
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts
    from solana.transaction import Transaction

try:
    from spl.token.constants import TOKEN_PROGRAM_ID
    from spl.token.instructions import (
        create_associated_token_account,
        create_mint,
        mint_to,
    )
except ImportError:
    import subprocess

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "spl-token"]
    )
    from spl.token.constants import TOKEN_PROGRAM_ID
    from spl.token.instructions import (
        create_associated_token_account,
        create_mint,
        mint_to,
    )


def generate_payer_keypair(filepath: str):
    """
    Generates a new Solana keypair and saves it to a file.

    Args:
        filepath (str): Path to save the generated keypair.

    Returns:
        str: The public key of the generated keypair.
    """
    # Generate a new keypair
    keypair = Keypair()
    secret_key = list(keypair.secret_key)

    # Ensure the directory exists
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Save the secret key to the file
    with open(filepath, "w") as file:
        json.dump(secret_key, file)

    # Set secure file permissions (Linux/macOS only)
    if os.name != "nt":  # Skip for Windows
        os.chmod(filepath, 0o600)

    print(f"Keypair saved to: {filepath}")
    print(f"Public Key: {keypair.public_key}")
    return str(keypair.public_key)


# # # Example Usage
# if __name__ == "__main__":
#     # payer_keypair_path = os.path.expanduser("~/.config/solana/id.json")
#     # public_key = generate_payer_keypair(payer_keypair_path)
#     # print(f"Payer's public key: {public_key}")


class TokenCreationError(Exception):
    """Custom exception for token creation failures."""


def load_keypair_from_file(filepath: str) -> Keypair:
    """
    Load a Keypair from a file containing a private key in JSON format.

    Args:
        filepath (str): Path to the keypair file.

    Returns:
        Keypair: The loaded Keypair object.

    Raises:
        FileNotFoundError: If the keypair file does not exist.
        ValueError: If the file content is invalid.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Keypair file not found: {filepath}")

    try:
        with open(filepath, "r") as file:
            secret_key = json.load(file)
        return Keypair.from_secret_key(bytes(secret_key))
    except Exception as e:
        raise ValueError(f"Failed to load keypair from file: {e}")


def launch_and_send_token(
    connection_url: str,
    payer_keypair_path: str,
    user_wallet_address: str,
    new_mint_supply: int,
    decimals: int = 9,
):
    """
    Launch a new token on Solana and send it to the user's wallet.

    Args:
        connection_url (str): Solana RPC URL.
        payer_keypair_path (str): Path to the payer's keypair file.
        user_wallet_address (str): The user's wallet address to receive tokens.
        new_mint_supply (int): Total supply for the new token.
        decimals (int): Decimal precision for the token (default is 9).

    Raises:
        TokenCreationError: If any step of the process fails.
    """
    logger.info("Initializing Solana client...")
    client = Client(connection_url)

    # Load the payer's Keypair
    logger.info("Loading payer keypair...")
    try:
        payer_keypair = load_keypair_from_file(payer_keypair_path)
    except Exception as e:
        raise TokenCreationError(f"Failed to load payer keypair: {e}")

    # Validate the user's wallet address
    try:
        user_wallet = PublicKey(user_wallet_address)
    except ValueError:
        raise TokenCreationError(
            f"Invalid user wallet address: {user_wallet_address}"
        )

    # Generate new mint keypair
    new_mint_keypair = Keypair()
    logger.info(
        f"Generated new token mint: {new_mint_keypair.public_key}"
    )

    # Step 1: Create the mint account
    try:
        logger.info("Creating mint account...")
        transaction = Transaction()
        transaction.add(
            create_mint(
                payer=payer_keypair.public_key,
                mint=new_mint_keypair.public_key,
                mint_authority=payer_keypair.public_key,
                decimals=decimals,
                program_id=TOKEN_PROGRAM_ID,
            )
        )
        response = client.send_transaction(
            transaction,
            payer_keypair,
            new_mint_keypair,
            opts=TxOpts(skip_preflight=True),
        )
        logger.success(
            f"Mint account created. Transaction signature: {response['result']}"
        )
    except Exception as e:
        raise TokenCreationError(
            f"Failed to create mint account: {e}"
        )

    # Step 2: Create the user's associated token account (ATA)
    try:
        logger.info(
            "Creating associated token account (ATA) for user..."
        )
        transaction = Transaction()
        transaction.add(
            create_associated_token_account(
                payer=payer_keypair.public_key,
                owner=user_wallet,
                mint=new_mint_keypair.public_key,
            )
        )
        response = client.send_transaction(
            transaction,
            payer_keypair,
            opts=TxOpts(skip_preflight=True),
        )
        ata_address = response["result"]
        logger.success(
            f"Associated token account created at: {ata_address}"
        )
    except Exception as e:
        raise TokenCreationError(
            f"Failed to create associated token account: {e}"
        )

    # Step 3: Mint tokens to the user's ATA
    try:
        logger.info(
            "Minting tokens to the user's associated token account..."
        )
        transaction = Transaction()
        transaction.add(
            mint_to(
                mint=new_mint_keypair.public_key,
                dest=ata_address,
                mint_authority=payer_keypair.public_key,
                amount=new_mint_supply * (10**decimals),
                program_id=TOKEN_PROGRAM_ID,
            )
        )
        response = client.send_transaction(
            transaction,
            payer_keypair,
            opts=TxOpts(skip_preflight=True),
        )
        logger.success(
            f"Minted {new_mint_supply} tokens. Transaction signature: {response['result']}"
        )
    except Exception as e:
        raise TokenCreationError(
            f"Failed to mint tokens to user: {e}"
        )

    logger.success(
        f"Token launched and sent successfully to user wallet: {user_wallet_address}"
    )


# payer_keypair_path = os.path.expanduser("~/.config/solana/id.json")
# public_key = generate_payer_keypair(payer_keypair_path)

# Example Usage
if __name__ == "__main__":
    try:
        launch_and_send_token(
            connection_url="https://api.mainnet-beta.solana.com",
            payer_keypair_path="~/.config/solana/id.json",
            user_wallet_address="UserWalletAddressHere",
            new_mint_supply=1_000_000,
            decimals=9,
        )
    except TokenCreationError as e:
        logger.error(f"Token creation failed: {e}")
