"""
xrpl_remittance.py
──────────────────
Phase 1 – Validate the XRPL testnet rail for a remittance concept.

This script demonstrates four things clearly:
  STEP 1 – Connect to the XRPL testnet
  STEP 2 – Fund or load a test wallet
  STEP 3 – Send XRP with a destination tag
  STEP 4 – Return and log the transaction hash

Usage
  python xrpl_remittance.py

  Optional env-overrides:
    SENDER_SEED    – reuse an existing funded sender wallet
    RECEIVER_ADDR  – send to a specific receiver address
    DEST_TAG       – destination tag (default: 593821)
    AMOUNT_XRP     – send amount in XRP (default: 3)

No mainnet. No real funds. No private keys stored.
"""

import os
import json
import logging
from datetime import datetime, timezone

from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops


# ═══════════════════════════════════════════════════════════
#  STEP 1 — CONNECT TO THE XRPL TESTNET
#
#  We point the client at Ripple's public testnet node.
#  This is a sandbox — no real money exists here.
#  Mainnet URL would be https://xrplcluster.com (never used here).
# ═══════════════════════════════════════════════════════════

TESTNET_URL   = "https://s.altnet.rippletest.net:51234"
EXPLORER_BASE = "https://testnet.xrpl.org/transactions"

AMOUNT_XRP = float(os.getenv("AMOUNT_XRP", "3"))
DEST_TAG   = int(os.getenv("DEST_TAG", "593821"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("xrpl_remittance")


def save_transaction(record: dict) -> None:
    """Append one JSON record per transaction to transactions.log."""
    with open("transactions.log", "a") as fh:
        fh.write(json.dumps(record) + "\n")


# ═══════════════════════════════════════════════════════════
#  STEP 2 — FUND OR LOAD A TEST WALLET
#
#  The testnet faucet gives us a wallet pre-loaded with fake XRP
#  automatically — no sign-up, no real money required.
#
#  To reuse an existing wallet: set SENDER_SEED in your environment.
#  To send to a fixed address:  set RECEIVER_ADDR in your environment.
# ═══════════════════════════════════════════════════════════

def get_sender_wallet(client: JsonRpcClient) -> Wallet:
    """
    Load an existing sender wallet from SENDER_SEED env var,
    or request a fresh one from the testnet faucet.
    """
    seed = os.getenv("SENDER_SEED")
    if seed:
        wallet = Wallet.from_seed(seed)
        log.info("[STEP 2] Loaded existing sender wallet: %s", wallet.classic_address)
        return wallet

    log.info("[STEP 2] Requesting a new SENDER wallet from the testnet faucet ...")
    wallet = generate_faucet_wallet(client, debug=False)
    log.info("[STEP 2] Sender wallet funded ✓  address=%s", wallet.classic_address)
    log.info("[STEP 2] Save this seed to reuse wallet: %s", wallet.seed)
    return wallet


def get_receiver_address(client: JsonRpcClient) -> str:
    """
    Use a fixed receiver address from RECEIVER_ADDR env var,
    or generate a second funded testnet wallet as the receiver.
    """
    addr = os.getenv("RECEIVER_ADDR")
    if addr:
        log.info("[STEP 2] Using provided receiver address: %s", addr)
        return addr

    log.info("[STEP 2] Requesting a new RECEIVER wallet from the testnet faucet ...")
    wallet = generate_faucet_wallet(client, debug=False)
    log.info("[STEP 2] Receiver wallet funded ✓  address=%s", wallet.classic_address)
    return wallet.classic_address


# ═══════════════════════════════════════════════════════════
#  STEP 3 — SEND XRP WITH A DESTINATION TAG
#
#  A Payment transaction is built with:
#    • account          – the sender's address
#    • destination      – the receiver's address
#    • amount           – in drops (1 XRP = 1,000,000 drops)
#    • destination_tag  – a numeric routing code, like a memo line,
#                         used to identify the recipient on the
#                         receiving end (e.g. exchange sub-account)
#
#  submit_and_wait() signs the transaction with the sender's key,
#  broadcasts it to the testnet, and blocks until the ledger
#  confirms it — usually within 4–6 seconds.
# ═══════════════════════════════════════════════════════════

def send_xrp(
    client: JsonRpcClient,
    sender: Wallet,
    receiver_address: str,
    amount_xrp: float,
    destination_tag: int,
) -> dict:
    """
    Build, sign, submit, and confirm an XRP Payment on the testnet.
    Returns the raw ledger result dict.
    """
    drops = xrp_to_drops(amount_xrp)  # Convert XRP → drops (no floats on the ledger)

    payment = Payment(
        account=sender.classic_address,   # Who is sending
        destination=receiver_address,      # Who is receiving
        amount=drops,                      # How much (in drops)
        destination_tag=destination_tag,   # Routing tag — identifies the recipient
    )

    log.info("[STEP 3] Submitting payment to testnet ...")
    log.info("[STEP 3]   Sender          : %s", sender.classic_address)
    log.info("[STEP 3]   Receiver        : %s", receiver_address)
    log.info("[STEP 3]   Amount          : %s XRP (%s drops)", amount_xrp, drops)
    log.info("[STEP 3]   Destination Tag : %s", destination_tag)

    # Sign locally, submit to testnet, wait for ledger validation
    response = submit_and_wait(payment, client, sender)
    return response.result


# ═══════════════════════════════════════════════════════════
#  STEP 4 — RETURN AND LOG THE TRANSACTION HASH
#
#  Once the ledger validates the transaction, it assigns a unique
#  hash (TX Hash) — a permanent, public fingerprint of the payment.
#
#  Anyone can paste this hash into the XRPL testnet explorer to
#  verify the sender, receiver, amount, destination tag, and status.
#
#  The full record is also saved to transactions.log as JSON.
# ═══════════════════════════════════════════════════════════

def build_and_log_record(result: dict, sender_address: str, receiver_address: str) -> dict:
    """
    Extract the transaction hash and all key fields from the ledger response.
    Save to transactions.log and return the full record.
    """
    tx_hash   = result["hash"]           # ← The unique transaction ID on the ledger
    timestamp = datetime.now(timezone.utc).isoformat()

    record = {
        "timestamp":       timestamp,
        "sender":          sender_address,
        "receiver":        receiver_address,
        "amount_xrp":      AMOUNT_XRP,
        "destination_tag": DEST_TAG,
        "tx_hash":         tx_hash,       # ← Returned here and printed in the receipt
        "ledger_index":    result.get("ledger_index"),
        "fee_drops":       result.get("Fee"),
        "validated":       result.get("validated", False),
        "explorer_url":    f"{EXPLORER_BASE}/{tx_hash}",
    }

    log.info("[STEP 4] Transaction hash returned : %s", tx_hash)
    log.info("[STEP 4] Explorer link             : %s", record["explorer_url"])

    save_transaction(record)
    log.info("[STEP 4] Full record saved to transactions.log")

    return record


# ═══════════════════════════════════════════════════════════
#  MAIN — Runs all four steps in sequence
# ═══════════════════════════════════════════════════════════

def main():
    print()
    print("═" * 60)
    print("  XRPL Remittance – Phase 1 – Testnet Rail Validation")
    print("═" * 60)
    print()

    # ── STEP 1 — Connect to testnet ───────────────────────
    client = JsonRpcClient(TESTNET_URL)
    log.info("[STEP 1] Connected to XRPL testnet: %s", TESTNET_URL)

    # ── STEP 2 — Fund / load wallets ──────────────────────
    sender           = get_sender_wallet(client)
    receiver_address = get_receiver_address(client)

    # ── STEP 3 — Send XRP with destination tag ────────────
    result = send_xrp(client, sender, receiver_address, AMOUNT_XRP, DEST_TAG)

    # ── STEP 4 — Return and log the transaction hash ──────
    record = build_and_log_record(result, sender.classic_address, receiver_address)

    # ── Receipt ───────────────────────────────────────────
    print()
    print("─" * 60)
    print("  ✅  Transaction confirmed on testnet ledger")
    print("─" * 60)
    print(f"  Timestamp       : {record['timestamp']}")
    print(f"  Sender          : {record['sender']}")
    print(f"  Receiver        : {record['receiver']}")
    print(f"  Amount          : {record['amount_xrp']} XRP")
    print(f"  Destination Tag : {record['destination_tag']}")
    print(f"  TX Hash         : {record['tx_hash']}")
    print(f"  Ledger Index    : {record['ledger_index']}")
    print(f"  Fee             : {record['fee_drops']} drops")
    print(f"  Validated       : {record['validated']}")
    print()
    print(f"  🔍  Explorer    : {record['explorer_url']}")
    print("─" * 60)
    print()


if __name__ == "__main__":
    main()