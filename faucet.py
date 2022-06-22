from bottle import post, request, run
import sqlite3
import subprocess

BANK = "paloma167rf0jmkkkqp9d4awa8rxw908muavqgghtw6tn"
AMOUNT = "1000000ugrain"

# TODO: DNS is preferred here.
API_NODE = "tcp://164.90.134.139:26657"

db = sqlite3.connect("faucet.db")
db.execute("CREATE TABLE IF NOT EXISTS addresses (address TEXT PRIMARY KEY, timestamp INTEGER)")

@post("/claim")
def index():
    # TODO(chase): Currently ignoring requests for "grain", only sending ugrain.
    #assert request.json["denom"] == "ugrain"
    address = request.json["address"]

    cur = db.cursor()
    if list(cur.execute("SELECT address FROM addresses WHERE address = ?", (address,))):
        return "funds previously sent, please wait a while"

    tx = subprocess.run([
        "palomad",
        "--node", API_NODE,
        "--fees", "200000ugrain",
        "-b", "block",
        "--chain-id", "paloma-testnet-5",
        "tx", "bank", "send", "-y",
        BANK,
        address,
        AMOUNT,
    ], capture_output=True)
    if tx.stderr:
        print(tx.stderr)
        return "failed"
    cur.execute("INSERT INTO addresses VALUES (?, date('now'))", (address,))
    db.commit()

    print(tx.stdout)
    return ""

run(host="localhost", port=8080)
