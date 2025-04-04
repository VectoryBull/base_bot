import dotenv
from web3 import Web3
import json

# --- CONFIGURATION ---
import os
dotenv.load_dotenv()
RPC_URL = os.getenv('RPC_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')
# Load ABI
with open('CompanyShipmentTracker.json') as f:
    contract_abi = json.load(f)['abi']
import time
import random
# --- SETUP ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=contract_abi)

contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=contract_abi)

def send_tx(fn):
    nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    tx = fn.build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': nonce,
        'gas': 300000,
        'gasPrice': w3.to_wei('2', 'gwei')
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"✅ TX confirmed: {tx_hash.hex()}")
    return receipt

def generate_shipments(n):
    return [
        (
            random.randint(60000, 120000),          # deliveryTime
            random.choice([True, True]),           # success
            random.randint(6000, 10000)             # feedbackScore
        )
        for _ in range(n)
    ]

# --- Push for Multiple Companies ---
company_list = [
    "HML Express",
    "Zeno Shipments",
    "Orbital Logistics",
    "FreightFox",
    "TurboTrek Cargo"
]

for company in company_list:
    entries = generate_shipments(5)
    print(f"\n📦 Sending entries for: {company}")
    for idx, (deliveryTime, success, feedbackScore) in enumerate(entries):
        print(f"  ↪ Entry {idx+1}: Delivery={deliveryTime}, Success={success}, Feedback={feedbackScore}")
        send_tx(
            contract.functions.addShipmentEntry(
                company,
                deliveryTime,
                success,
                feedbackScore
            )
        )
        # time.sleep(1.2)  # slight delay for rate-limited nodes

print("\n✅ All companies processed.")