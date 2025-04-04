import os
import json
import secrets
from dotenv import load_dotenv

from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    
    EthAccountWalletProvider,
    EthAccountWalletProviderConfig,
    
    cdp_api_action_provider,
    erc20_action_provider,
    pyth_action_provider,
    wallet_action_provider,
    weth_action_provider,
)

from eth_account import Account
from coinbase_agentkit.network import NETWORK_ID_TO_CHAIN_ID, NETWORK_ID_TO_CHAIN, CHAIN_ID_TO_NETWORK_ID


"""
AgentKit Configuration

This file serves as the entry point for configuring AgentKit tools and wallet providers.
It handles wallet setup, persistence, and initializes AgentKit with the appropriate providers.

# Key Steps to Configure AgentKit:

1. Set up your WalletProvider:
   - Learn more: https://github.com/coinbase/agentkit/tree/main/python/agentkit#evm-wallet-providers

2. Set up your Action Providers:
   - Action Providers define what your agent can do.  
   - Choose from built-in providers or create your own:
     - Built-in: https://github.com/coinbase/agentkit/tree/main/python/coinbase-agentkit#create-an-agentkit-instance-with-specified-action-providers
     - Custom: https://github.com/coinbase/agentkit/tree/main/python/coinbase-agentkit#creating-an-action-provider

# Next Steps:

- Explore the AgentKit README: https://github.com/coinbase/agentkit
- Learn more about available WalletProviders & Action Providers.
- Experiment with custom Action Providers for your unique use case.

## Want to contribute?
Join us in shaping AgentKit! Check out the contribution guide:  
- https://github.com/coinbase/agentkit/blob/main/CONTRIBUTING.md
- https://discord.gg/CDP
"""

# Configure a file to persist wallet data
wallet_data_file = "wallet_data.txt"

def prepare_agentkit():
    """Initialize Ethereum Account Wallet Provider and return tools."""

    
    # Initialize WalletProvider
    private_key = os.getenv("PRIVATE_KEY")
    
    if not private_key:
        if os.path.exists(wallet_data_file):
            try:
                with open(wallet_data_file) as f:
                    wallet_data = json.load(f)
                    private_key = wallet_data.get("private_key")
                    print("Found private key in wallet_data.txt")
            except Exception as e:
                print(f"Error reading wallet data: {e}")
        
        if not private_key:
            private_key = "0x" + secrets.token_hex(32)
            with open(wallet_data_file, "w") as f:
                json.dump({"private_key": private_key}, f)
            print("Created new private key and saved to wallet_data.txt")
            print("We recommend you save this private key to your .env file and delete wallet_data.txt afterwards.")

    assert private_key.startswith("0x"), "Private key must start with 0x hex prefix"
    
    account = Account.from_key(private_key)

    # Get chain configuration
    chain_id = os.getenv("CHAIN_ID")
    rpc_url = os.getenv("RPC_URL")
    network = os.getenv("NETWORK")

    if chain_id and rpc_url:
        pass
    elif network:
        chain_id = NETWORK_ID_TO_CHAIN_ID.get(network)
        if not chain_id:
            raise ValueError(f"Unknown network ID: {network}")
        
        if not rpc_url:
            chain = NETWORK_ID_TO_CHAIN[network]
            print("DEBUG: dir(chain) =", dir(chain))

            rpc_url = chain.rpc_urls['default'].http[0]

    elif chain_id:
        network = CHAIN_ID_TO_NETWORK_ID.get(chain_id)
        if network:
            chain = NETWORK_ID_TO_CHAIN[network]
            rpc_url = chain["rpc_urls"]["default"]["http"][0]
        else:
            raise ValueError("When using chain_id, you must also provide an RPC_URL if the chain is not recognized")
    else:
        print("No network configuration provided. Defaulting to Base Sepolia...")
        network = "base-sepolia"
        chain_id = NETWORK_ID_TO_CHAIN_ID[network]
        chain = NETWORK_ID_TO_CHAIN[network]
        rpc_url = chain["rpc_urls"]["default"]["http"][0]

    wallet_provider = EthAccountWalletProvider(
        config=EthAccountWalletProviderConfig(
            account=account,
            chain_id=chain_id,
            rpc_url=rpc_url
        )
    )
    

    # Initialize AgentKit
    agentkit = AgentKit(AgentKitConfig(
        wallet_provider=wallet_provider,
        action_providers=[
            
            cdp_api_action_provider(),
            erc20_action_provider(),
            wallet_action_provider(),
            weth_action_provider(),
        ]
    ))

    

    return agentkit