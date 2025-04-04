import dotenv
from web3 import Web3
import json
import os
# --- CONFIGURATION ---
dotenv.load_dotenv()
ABI_PATH = "CompanyShipmentTracker.json"
RPC_URL = os.getenv('RPC_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')
# --- SETUP ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
with open(ABI_PATH) as f:
    contract_abi = json.load(f)["abi"]
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=contract_abi)

# --- Query Company Metrics ---
def print_metrics(company_name):
    metrics = contract.functions.getCompanyMetrics(company_name).call()

    print(f"""
📊 Metrics for '{metrics[0]}'
──────────────────────────────
Total Deliveries       : {metrics[1]}
Success Rate           : {metrics[2] / 100:.2f}%
Avg Feedback Score     : {metrics[3] / 100:.2f}%
Avg Delivery Score     : {metrics[4]} / 100
Successful Deliveries  : {metrics[5]}
Unsuccessful Deliveries: {metrics[6]}
""")

# --- Query Company Shipment Entries ---
def print_entries(company_name):
    entries = contract.functions.getCompanyEntries(company_name).call()
    print(f"📦 {len(entries)} Shipment Entries for '{company_name}':")
    for i, e in enumerate(entries):
        print(f"  #{i+1}: Time={e[0]}s | Success={e[1]} | Feedback={e[2]/100:.2f}% | Timestamp={e[3]}")

# === MAIN ===
company_names = [
    "Thunderhorn Express",
    "Zeno Shipments",
    "Orbital Logistics",
    "FreightFox",
    "TurboTrek Cargo"
]

for name in company_names:
    try:
        print_metrics(name)
        print_entries(name)
        print("─────────────────────────────────────────────\n")
    except Exception as e:
        print(f"⚠️ Could not fetch data for '{name}': {e}")
