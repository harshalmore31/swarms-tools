import subprocess
import sys
from loguru import logger
from solana.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID


# Ensure required packages are installed
def ensure_packages():
    required_packages = ["solana", "spl-token", "loguru"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            logger.info(f"Package {package} not found. Installing...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package]
            )


# Lazy load Solana client
def get_client(url: str):
    logger.info(f"Connecting to Solana cluster at {url}")
    return AsyncClient(url)


# Create a token using pure Solana
async def create_pure_solana_token(
    initial_supply: int, decimals: int
):
    ensure_packages()

    # Connect to Solana
    solana_url = "https://api.devnet.solana.com"  # Or use mainnet for production
    client = get_client(solana_url)

    # Generate keypairs for mint and owner
    mint_keypair = Keypair.generate()
    owner_keypair = Keypair.generate()

    # Airdrop SOL to the owner (only on devnet)
    logger.info("Requesting airdrop...")
    await client.request_airdrop(
        owner_keypair.public_key, 2_000_000_000
    )  # 2 SOL

    # Create the token mint
    logger.info("Creating token mint...")
    token = await AsyncToken.create_mint(
        connection=client,
        payer=owner_keypair,
        mint_authority=owner_keypair.public_key,
        freeze_authority=owner_keypair.public_key,
        decimals=decimals,
        mint=mint_keypair,
        program_id=TOKEN_PROGRAM_ID,
    )

    # Create an associated token account for the owner
    logger.info("Creating token account...")
    token_account = await token.create_associated_token_account(
        owner_keypair.public_key
    )

    # Mint initial supply to the owner
    logger.info(f"Minting {initial_supply} tokens...")
    await token.mint_to(
        dest=token_account,
        mint_authority=owner_keypair,
        amount=initial_supply,
    )

    # Print token details
    logger.info(f"Token Mint Address: {mint_keypair.public_key}")
    logger.info(f"Owner Token Account Address: {token_account}")

    # Close connection
    await client.close()


# # Run the function with custom supply and decimals
# if __name__ == "__main__":
#     logger.info("Starting token creation script...")
#     initial_supply = 1_000_000 * (10 ** 9)  # Adjust supply as needed
#     decimals = 9  # Number of decimal places for the token
#     asyncio.run(create_pure_solana_token(initial_supply=initial_supply, decimals=decimals))
