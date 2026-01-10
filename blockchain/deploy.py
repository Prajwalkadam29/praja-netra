import json
from web3 import Web3
from solcx import compile_standard, install_solc
import os

# 1. Setup Web3 and Account (Ganache)
RPC_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
# Use the first account provided by Ganache
private_key = "0x879be279c458418c8fe71644ae83c358c787dd0ba21f067cddc758ea471f1f7c"
account_address = w3.eth.account.from_key(private_key).address

# 2. Compile Solidity
print("🔨 Compiling Smart Contract...")
install_solc("0.8.0")
with open("contracts/Integrity.sol", "r") as file:
    contract_source_code = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Integrity.sol": {"content": contract_source_code}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode", "evm.sourceMap"]}}},
    },
    solc_version="0.8.0",
)

# 3. Extract ABI and Bytecode
abi = compiled_sol["contracts"]["Integrity.sol"]["PrajaNetraIntegrity"]["abi"]
bytecode = compiled_sol["contracts"]["Integrity.sol"]["PrajaNetraIntegrity"]["evm"]["bytecode"]["object"]

# 4. Deploy to Ganache
print("🚀 Deploying to Blockchain...")
IntegrityContract = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(account_address)

transaction = IntegrityContract.constructor().build_transaction({
    "chainId": 1337,
    "gasPrice": w3.eth.gas_price,
    "from": account_address,
    "nonce": nonce,
})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"✅ Contract Deployed Successfully!")
print(f"📍 CONTRACT_ADDRESS: {tx_receipt.contractAddress}")