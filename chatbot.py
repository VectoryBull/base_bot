import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from web3 import Web3
from agents.run import Runner

from contract.query_logistics_data import query_logistics_data
from create_agent import create_agent
import logging as L
load_dotenv()
from cdp import *


# === CONFIG ===
RPC_URL = os.getenv("RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
ABI_PATH = os.getenv("ABI_PATH", "contract/CompanyShipmentTracker.json")

# === WEB3 ===
w3 = Web3(Web3.HTTPProvider(RPC_URL))
with open(ABI_PATH) as f:
    abi = json.load(f)["abi"]
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)

# === AGENT ===
agent_executor, config = create_agent()

# === FASTAPI ===
app = FastAPI()

class QueryRequest(BaseModel):
    prompt: str
    name: str = None

@app.get("/")
def root():
    return {"message": "Shipping Quality Assistant API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
async def query_intent(req: QueryRequest):
    user_prompt = req.prompt.strip()

    # === Step 1: Detect user intent ===
    thought = (
        "Your name is Vector! You are a helpful assistant for a shipping quality company.\n"
        "Decide the user's intent. Options:\n"
        "- advice\n"
        "- find_shipment_company\n"
        "- shipment_data\n"
        "\n"
        f"USER PROMPT: {user_prompt}"
    )

    try:
        result = await Runner.run(agent_executor, thought)
        L.info(result)
        intent_output = result.final_output.lower()
        match True:
            case _ if "find_shipment_company" in intent_output:
                intent = "find_shipment_company"
            case _ if "shipment_data" in intent_output:
                intent = "shipment_data"
            case _:
                intent = "advice"
        L.info(f"Detected intent: {intent}")

        if intent == "find_shipment_company":
            companies = contract.functions.getAllCompanies().call()
            if not companies:
                return {"reply": "Sorry, no company records found on-chain yet."}

            top = sorted(companies, key=lambda c: (c[2], c[3]), reverse=True)[:3]
            top_companies = [
                {
                    "name": c[0],
                    "successRate": round(c[2] , 2),
                    "feedbackScore": round(c[3], 2),
                    "deliveryScore": c[4],
                    "deliveries": c[1]
                }
                for c in top
            ]
            print(top_companies)
            L.info(
                f"Top 3 companies: {json.dumps(top_companies, indent=2)}"
            )

            re_thought = (
                "You're a shipping assistant helping a user find a reliable shipping company.\n"
                f"Based on this data: {json.dumps(top_companies, indent=2)}\n"
                "Generate a friendly, human-readable recommendation. NEVER use h tags! You CAN use bold"
            )
            L.info(re_thought)
            final = await Runner.run(agent_executor, re_thought)
            return {"reply": final.final_output}
        elif intent == "shipment_data":
            data = query_logistics_data()
            thought = (
                "Your name is Vector! You are a helpful assistant for a shipping quality company.\n"
                "Generate a friendly, human-readable response for the user.\n"
                "You have a histogram of which user is interested answer his question clear and shortly like max 2-3 sentences.\n"
                f"USER QUERY: {user_prompt} \n"
                f"basen on the data \n"
                f"DATA: {data}"
            )
            final = await Runner.run(agent_executor, thought)
            return {"reply": final.final_output}
        else:
            thought = (
                "Your name is Vector! You are a helpful assistant for a shipping quality company.\n"
                "Give a short, friendly advice to the user.\n"
                f"USER QUERY: {user_prompt}"
            )
            final = await Runner.run(agent_executor, thought)
            return {"reply": final.final_output}

    except Exception as e:
        L.exception("Error in query_intent")
        return {"reply": "Sorry, something went wrong while processing your request."}
