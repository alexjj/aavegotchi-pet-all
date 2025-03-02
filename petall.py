import sys
import time
from web3 import Web3
from web3.auto import w3
from eth_account import Account

rpc = ""
private_key = ""
aavegotchi_abi = ""
aavegotchi_diamond = ""
with open("matic_rpc.secret", "r") as reader:
    rpc = reader.read().strip()

with open("abi.json", "r") as reader:
    aavegotchi_abi = reader.read().strip()

with open("aavegotchiDiamond.txt", "r") as reader:
    aavegotchi_diamond = reader.read().strip()

with open("private_key.secret", "r") as reader:
    private_key = reader.read().strip()

web3 = Web3(Web3.HTTPProvider(rpc))
from web3.middleware import geth_poa_middleware
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

aavegotchi_diamond = web3.toChecksumAddress(aavegotchi_diamond)

acct = Account.privateKeyToAccount(private_key)
ether_address = acct.address

contract = web3.eth.contract(address=aavegotchi_diamond, abi=aavegotchi_abi)
gotchis = contract.functions.tokenIdsOfOwner(ether_address).call()

print("Attempting to pet gotchis with the following IDs:")
print(f"{gotchis}")

if gotchis:
    aavegotchi_details = contract.functions.getAavegotchi(gotchis[0]).call()
    twelve_hours = 12 * 60 * 60
    next_interact_time = aavegotchi_details[13] + twelve_hours
    print(f"Next interaction time: {next_interact_time}")
    print(f"Current time: {time.time()}")
    time_till = (next_interact_time - time.time())
    print(f"Time till next interaction: {time_till / (60*60)} hours.")
    if time_till > 0:
        print(f"Sleeping for {time_till + 30} seconds")
        time.sleep(time_till + 30)
    nonce = web3.eth.get_transaction_count(ether_address)
    pet = contract.functions.interact(gotchis).buildTransaction({
        "chainId":137,
        "gasPrice": w3.toWei("1", "gwei"),
        "nonce": nonce
    })
    signed_txn = web3.eth.account.sign_transaction(pet, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction).hex()
    print("interact() called. Transaction ID:")
    print(f"https://explorer-mainnet.maticvigil.com/tx/{tx_hash}")
