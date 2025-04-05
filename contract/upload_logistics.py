import os
import json
import dotenv
from web3 import Web3
import random
import time

# Load .env
dotenv.load_dotenv()

# Configs
RPC_URL = os.getenv('RPC_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')
CONTRACT_ADDRESS = os.getenv('LOGISTICS_CONTRACT_ADDRESS')

# Setup Web3
web3 = Web3(Web3.HTTPProvider(RPC_URL))
assert web3.is_connected(), "Failed to connect to the RPC"

# Load ABI
with open('LogisticsDataStorage.json') as f:
    abi = json.load(f)['abi']

contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)

# Use a static shipment ID
shipment_id = web3.keccak(text=str(random.randint(100000, 999999)))

# Create the delivery if not yet created
def create_delivery():
    tx = contract.functions.createDelivery(
        shipment_id,
        "Berlin",
        "Paris",
        "Vehicle"
    ).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        'gas': 300000,
        'gasPrice': web3.eth.gas_price,
    })
    signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
    print("🚚 createDelivery() sent, tx:", web3.to_hex(tx_hash))
    web3.eth.wait_for_transaction_receipt(tx_hash)

# Push a fake sensor reading
def push_sensor_data():
    for _ in range(20):  # Push 20 fake entries
        temp = random.randint(2200, 2700)     # e.g., 22.00°C to 27.00°C
        humid = random.randint(4000, 6000)    # e.g., 40.00% to 60.00%
        vib = random.randint(0, 500)
        acc_x = random.randint(-100, 100)
        acc_y = random.randint(-100, 100)
        acc_z = 9800 + random.randint(-100, 100)

        nonce = web3.eth.get_transaction_count(ACCOUNT_ADDRESS)

        tx = contract.functions.submitSensorData(
            shipment_id,
            temp,
            humid,
            vib,
            acc_x,
            acc_y,
            acc_z
        ).build_transaction({
            'from': ACCOUNT_ADDRESS,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': web3.eth.gas_price,
        })

        signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"📡 Pushed sensor data tx: {web3.to_hex(tx_hash)}")
        web3.eth.wait_for_transaction_receipt(tx_hash)

        time.sleep(1)  # Optional: slight delay to simulate streaming data

# 🚀 Run everything
if __name__ == "__main__":
    try:
        print("🚀 Creating delivery...")
        create_delivery()
    except Exception as e:
        print("⚠️ Likely already exists, skipping createDelivery():", e)

    print("📈 Pushing fake sensor data...")
    push_sensor_data()
