import os
import json
from web3 import Web3
from datetime import datetime
from dotenv import load_dotenv
from web3._utils.events import get_event_data

def query_logistics_data():
    # === Load environment ===
    load_dotenv()

    RPC_URL = os.getenv('RPC_URL')
    CONTRACT_ADDRESS = os.getenv('LOGISTICS_CONTRACT_ADDRESS')
    ABI_PATH = os.path.join(os.path.dirname(__file__), 'LogisticsDataStorage.json')

    # === Connect to Web3 ===
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    assert web3.is_connected(), "❌ RPC connection failed."

    # === Load ABI ===
    with open(ABI_PATH) as f:
        abi = json.load(f)["abi"]

    contract = web3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=abi
    )

    # === Find the DeliveryCreated event ABI ===
    event_abi = next((item for item in abi if item.get("type") == "event" and item.get("name") == "DeliveryCreated"), None)
    if not event_abi:
        raise RuntimeError("❌ Could not find DeliveryCreated event ABI.")

    # === Fetch logs manually ===
    try:
        topic = Web3.keccak(text="DeliveryCreated(bytes32,address)").hex()
        logs = web3.eth.get_logs({
            "fromBlock": 0,
            "toBlock": "latest",
            "address": Web3.to_checksum_address(CONTRACT_ADDRESS),
            "topics": ['0x'+str(topic)]
        })

        shipment_ids = []
        for log in logs:
            decoded = get_event_data(web3.codec, event_abi, log)
            shipment_ids.append(decoded["args"]["shipmentId"])

        shipment_ids = list(set(shipment_ids))  # De-duplicate

    except Exception as e:
        raise RuntimeError(f"❌ Failed to fetch events: {e}")

    if not shipment_ids:
        return []

    all_data = []

    for shipment_id in shipment_ids:
        shipment_hex = shipment_id.hex()

        try:
            sensor_data = contract.functions.getDeliveryData(shipment_id).call()
        except Exception as e:
            continue

        if not sensor_data:
            continue

        parsed = []
        for entry in sensor_data:
            parsed.append({
                "timestamp": datetime.utcfromtimestamp(entry[0]).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "temperature": entry[1] / 100.0,
                "humidity": entry[2] / 100.0,
                "vibrations": entry[3],
                "accelX": entry[4],
                "accelY": entry[5],
                "accelZ": entry[6]
            })

        all_data.append({
            "shipmentId": shipment_hex,
            "records": parsed
        })

    return all_data