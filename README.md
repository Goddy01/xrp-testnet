# XRPL Remittance – Phase 1

> **What this is:** A simple test that proves money can move across the XRP Ledger — fast, tracked, and verifiable.
> Think of it as a dry run of the remittance rail before we build the full product around it.

**Important:** This runs entirely on the XRP *testnet* — a sandbox environment made for testing. No real money is involved at any point.

---

## What happens when you run this

1. Two test wallets are created and automatically loaded with fake XRP (courtesy of the testnet)
2. A payment is sent from one wallet to the other — with a destination tag (like a memo line that tells the receiving side who the money is for)
3. The transaction is confirmed on the ledger and you get back a **transaction hash** — a unique ID you can look up to verify it happened
4. Everything is logged: who sent, who received, how much, when, and the confirmation link

That's it. The whole point is to confirm the rails work before we build anything on top of them.

---

## Before you start — what you'll need

You need three free things installed on your computer. If you already have them, skip ahead.

### 1. Git
Git is what lets you download ("clone") this project from GitHub.

- **Mac:** Open Terminal and type `git --version`. If it's not installed, your Mac will prompt you to install it automatically.
- **Windows:** Download from [git-scm.com](https://git-scm.com/download/win) and run the installer. All default settings are fine.

### 2. Python
Python is the programming language this script is written in.

- Go to [python.org/downloads](https://www.python.org/downloads/)
- Download the latest version (3.9 or higher)
- **Windows users:** During installation, check the box that says **"Add Python to PATH"** — this is easy to miss

To check it worked, open Terminal (Mac) or Command Prompt (Windows) and type:
```
python3 --version
```

or 
```
python --version
```

You should see something like `Python 3.12.0`.

### 3. pip
pip is Python's built-in tool for installing libraries. It comes with Python automatically — you don't need to do anything extra.

---

## Setup — do this once

Open **Terminal** (Mac) or **Command Prompt** (Windows) and run these commands one at a time, pressing Enter after each.

Move into the project folder:
```
cd xrp-testnet
```

### Step 2 — Create a clean workspace (recommended)
This keeps the project's tools separate from anything else on your computer:
```
python3 -m venv .venv
```

Then activate it:

- **Mac/Linux:**
  ```
  source .venv/bin/activate
  ```
- **Windows:**
  ```
  .venv\Scripts\activate
  ```
  - **Git Bash:**
  ```
  source .venv/Scripts/activate
  ```

You'll know it worked when you see `(.venv)` appear at the start of your terminal line.

### Step 3 — Install required packages
```
pip install -r requirements.txt
```
This installs the needed library which is just xrpl-py.

---

## Running the script

Once setup is done, this is all you ever need to type:

```
python xrpl_remittance.py
```

Wait about 10–15 seconds. The script will connect to the testnet, create wallets, send the payment, and print your receipt.

---

## Reading the output

When it finishes, you'll see something like this:

```
──────────────────────────────────────────────────────
  ✅  Transaction confirmed on testnet ledger
──────────────────────────────────────────────────────
  Timestamp       : 2026-04-30T09:00:10+00:00
  Sender          : rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh
  Receiver        : rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe
  Amount          : 10.0 XRP
  Destination Tag : 12345
  TX Hash         : A1B2C3D4E5F6…
  Ledger Index    : 3847291
  Fee             : 12 drops
  Validated       : True

  🔍  Explorer    : https://testnet.xrpl.org/transactions/A1B2C3D4...
──────────────────────────────────────────────────────
```

Here's what each line means:

| Field | What it means |
|---|---|
| **Timestamp** | When the transaction happened (UTC time) |
| **Sender** | The wallet the XRP was sent from |
| **Receiver** | The wallet the XRP was sent to |
| **Amount** | How much XRP was sent (10 by default) |
| **Destination Tag** | A routing code — like a memo line — so the receiver knows who it's for |
| **TX Hash** | A unique ID for this transaction, permanently recorded on the ledger |
| **Ledger Index** | Which "block" in the chain this was recorded in |
| **Fee** | The tiny network processing fee (12 drops = 0.000012 XRP — basically free) |
| **Validated** | `True` means the network confirmed it — it's done |
| **Explorer link** | Click this to see the transaction live on the testnet ledger |

---

## Save your sender wallet (optional but useful)

The first time you run the script, you'll see a line like:

```
(save this seed to reuse: sEdT…)
```

Copy that seed and save it somewhere safe (a notes app is fine — it's testnet, so there's no real value). On future runs, you can reuse the same wallet instead of creating a new one each time:

**Mac/Linux:**
```
SENDER_SEED=sEdT… python xrpl_remittance.py
```
**Windows Command Prompt:**
```
set SENDER_SEED=sEdT… && python xrpl_remittance.py
```

---

## The transaction log

Every time you run the script, a record is saved to a file called `transactions.log` in the same folder. This is where every send is recorded — sender, receiver, amount, tag, hash, and timestamp — ready to be imported into a database or dashboard when Phase 2 is built.

---

## Troubleshooting

**"python3: command not found"**
Python isn't installed, or wasn't added to your PATH during installation. Revisit the Python step in Prerequisites above.

**"No module named xrpl"**
The library isn't installed yet, or your virtual environment isn't active. Make sure you ran `pip install xrpl-py` and that you see `(.venv)` in your terminal.

**The script just hangs / times out**
The testnet faucet is occasionally slow. Wait 30 seconds and try again. If it keeps failing, the testnet may be briefly down — try again in a few minutes.

**"git: command not found"**
Git isn't installed. See the Git step in Prerequisites above.

---

## Helpful links

| Link | What it's for |
|---|---|
| [XRPL Testnet Explorer](https://testnet.xrpl.org) | Look up any transaction by its hash |
| [XRPL Testnet Faucet](https://faucet.altnet.rippletest.net/accounts) | Manually create and fund a testnet wallet in your browser |
| [What is a destination tag?](https://xrpl.org/source-and-destination-tags.html) | Official explainer on how routing tags work |

---