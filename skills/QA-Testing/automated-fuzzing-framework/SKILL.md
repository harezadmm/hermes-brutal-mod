---
name: automated-fuzzing-framework
description: Build and deploy fuzzing infrastructure for vulnerability discovery
version: 1.0.0
author: harezadmm
tags: [fuzzing, afl, libfuzzer, testing, vulnerability, security]
---

# Automated Fuzzing Framework

## When to Use
Setting up automated fuzzing infrastructure to discover vulnerabilities, crashes, and security bugs in applications (binaries, APIs, file parsers, protocols).

## Prerequisites
- Target application (binary, library, or service)
- Linux system (fuzzing works best on Linux)
- Basic understanding of compilation and instrumentation
- Storage for corpus and crash samples

## Fuzzing Tools

### 1. AFL++ (American Fuzzy Lop)
Coverage-guided binary fuzzing, excellent for CLI tools.

### 2. libFuzzer
LLVM-based in-process fuzzer, good for libraries.

### 3. Honggfuzz
Multi-threaded fuzzer with hardware-assisted feedback.

### 4. Radamsa
Mutation-based fuzzer for file formats.

### 5. Boofuzz
Network protocol fuzzer (Sulley successor).

### 6. ffuf/wfuzz
Web application fuzzing.

## Procedure

### Step 1: AFL++ Setup and Compilation

**Install AFL++:**
```bash
# Install dependencies
apt-get update
apt-get install -y build-essential python3-dev automake cmake git flex bison libglib2.0-dev libpixman-1-dev python3-setuptools cargo libgtk-3-dev

# Clone and build AFL++
git clone https://github.com/AFLplusplus/AFLplusplus
cd AFLplusplus
make distrib
sudo make install

# Verify installation
afl-fuzz --version
```

**Compile target with AFL++ instrumentation:**
```bash
# Example: Fuzzing a PNG parser
git clone https://github.com/glennrp/libpng
cd libpng

# Configure with AFL compiler
export CC=afl-clang-fast
export CXX=afl-clang-fast++
export AFL_USE_ASAN=1  # Enable AddressSanitizer for better crash detection

./configure --disable-shared
make clean
make

# Test if instrumentation worked
afl-clang-fast test.c -o test_fuzz
```

**Prepare seed corpus:**
```bash
# Create input directory with sample files
mkdir -p input_corpus
mkdir -p output_crashes

# Add seed files (valid PNG images)
cp /usr/share/pixmaps/*.png input_corpus/
wget https://sample-files.com/sample.png -P input_corpus/

# Minimize corpus (remove redundant files)
afl-cmin -i input_corpus -o input_corpus_min -- ./pngtest @@
```

**Run AFL fuzzer:**
```bash
# Single instance
afl-fuzz -i input_corpus_min -o output_crashes -M fuzzer01 -- ./pngtest @@

# Multi-core fuzzing (parallel instances)
# Terminal 1 (master)
afl-fuzz -i input_corpus_min -o sync_dir -M master -- ./pngtest @@

# Terminal 2-4 (slaves)
afl-fuzz -i - -o sync_dir -S slave01 -- ./pngtest @@
afl-fuzz -i - -o sync_dir -S slave02 -- ./pngtest @@
afl-fuzz -i - -o sync_dir -S slave03 -- ./pngtest @@

# Monitor status
afl-whatsup sync_dir
```

### Step 2: libFuzzer Integration

**Create fuzz target (C++):**
```cpp
// fuzz_target.cpp
#include <stdint.h>
#include <stddef.h>
#include <string>
#include "vulnerable_library.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // Convert raw bytes to string
    std::string input(reinterpret_cast<const char*>(data), size);
    
    // Call vulnerable function
    try {
        parse_xml(input);  // Function we're fuzzing
    } catch (...) {
        // Ignore exceptions, we want crashes only
    }
    
    return 0;
}
```

**Compile with libFuzzer:**
```bash
# Compile with clang and libFuzzer
clang++ -g -O1 -fsanitize=fuzzer,address,undefined \
    fuzz_target.cpp vulnerable_library.cpp \
    -o fuzz_xml

# Run fuzzer
./fuzz_xml corpus/ -dict=xml.dict -max_len=4096

# With options
./fuzz_xml corpus/ \
    -max_total_time=3600 \
    -timeout=10 \
    -rss_limit_mb=2048 \
    -dict=xml.dict \
    -jobs=8 \
    -workers=8
```

**Create dictionary for better mutations:**
```bash
# xml.dict
"<?xml"
"version="
"encoding="
"<tag>"
"</tag>"
"CDATA"
"&lt;"
"&gt;"
"&#"
```

### Step 3: API Fuzzing with RESTler

**Install RESTler:**
```bash
# Install .NET SDK
wget https://dot.net/v1/dotnet-install.sh
bash dotnet-install.sh --channel 7.0

# Clone and build RESTler
git clone https://github.com/microsoft/restler-fuzzer
cd restler-fuzzer
python3 ./build-restler.py --dest_dir ./restler_bin
```

**Fuzz REST API from OpenAPI spec:**
```bash
# Download or create OpenAPI spec
cat > api_spec.json << 'EOF'
{
  "openapi": "3.0.0",
  "info": {"title": "Vulnerable API", "version": "1.0"},
  "servers": [{"url": "http://target-api.com/api"}],
  "paths": {
    "/users/{id}": {
      "get": {
        "parameters": [
          {"name": "id", "in": "path", "required": true, "schema": {"type": "integer"}}
        ]
      }
    },
    "/upload": {
      "post": {
        "requestBody": {
          "content": {
            "multipart/form-data": {
              "schema": {
                "type": "object",
                "properties": {
                  "file": {"type": "string", "format": "binary"}
                }
              }
            }
          }
        }
      }
    }
  }
}
EOF

# Compile API specification
./restler_bin/restler/Restler compile --api_spec api_spec.json

# Test mode (quick validation)
./restler_bin/restler/Restler test --grammar_file Compile/grammar.py --dictionary_file Compile/dict.json --settings Compile/engine_settings.json

# Fuzz mode (comprehensive testing)
./restler_bin/restler/Restler fuzz --grammar_file Compile/grammar.py --dictionary_file Compile/dict.json --settings Compile/engine_settings.json --time_budget 24

# Check results
cat Test/ResponseBuckets/errorBucket.txt
cat Fuzz/bug_buckets/*.txt
```

### Step 4: Network Protocol Fuzzing with Boofuzz

**Install boofuzz:**
```bash
pip3 install boofuzz
```

**Create fuzzing script for network protocol:**
```python
#!/usr/bin/env python3
# fuzz_protocol.py
from boofuzz import *

# Define protocol structure
def build_http_request():
    s_initialize("HTTP Request")
    
    # Method
    s_string("GET", fuzzable=True)
    s_delim(" ")
    
    # Path
    s_string("/", fuzzable=False)
    s_string("index", fuzzable=True)
    s_string(".html", fuzzable=True)
    s_delim(" ")
    
    # Version
    s_string("HTTP/1.1", fuzzable=False)
    s_delim("\r\n")
    
    # Headers
    s_string("Host: ", fuzzable=False)
    s_string("target.com", fuzzable=True)
    s_delim("\r\n")
    
    s_string("User-Agent: ", fuzzable=False)
    s_string("Mozilla/5.0", fuzzable=True)
    s_delim("\r\n")
    
    s_string("Content-Length: ", fuzzable=False)
    s_size("body", output_format="ascii", fuzzable=True)
    s_delim("\r\n\r\n")
    
    # Body
    s_block_start("body")
    s_string("param1=", fuzzable=False)
    s_string("value1", fuzzable=True)
    s_block_end("body")

def main():
    session = Session(
        target=Target(
            connection=SocketConnection("192.168.1.100", 80, proto='tcp')
        ),
        sleep_time=0.5
    )
    
    # Add protocol definition
    build_http_request()
    
    # Connect graph
    session.connect(s_get("HTTP Request"))
    
    # Start fuzzing
    session.fuzz()

if __name__ == "__main__":
    main()
```

**Run protocol fuzzer:**
```bash
python3 fuzz_protocol.py

# Monitor crashes
tail -f boofuzz-results/run-*/crash-*.txt
```

### Step 5: Web Application Fuzzing

**ffuf - Fast web fuzzer:**
```bash
# Install ffuf
go install github.com/ffuf/ffuf/v2@latest

# Directory fuzzing
ffuf -u https://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302

# Parameter fuzzing
ffuf -u https://target.com/api?param=FUZZ -w payloads.txt -mc all -fc 404

# POST data fuzzing
ffuf -u https://target.com/login -X POST -d "username=admin&password=FUZZ" -w passwords.txt -mc 200 -fr "Invalid"

# Header injection
ffuf -u https://target.com/ -H "X-Custom-Header: FUZZ" -w xss_payloads.txt -mc all

# SQL injection fuzzing
ffuf -u https://target.com/search?q=FUZZ -w sqli_payloads.txt -mc 200 -fw 100-200

# File upload fuzzing (extension bypass)
ffuf -u https://target.com/upload -X POST -F "file=@test.FUZZ" -w extensions.txt -mc 200

# Virtual host fuzzing
ffuf -u https://target.com/ -H "Host: FUZZ.target.com" -w subdomains.txt -mc all -fc 404
```

**Custom fuzzing script with payloads:**
```python
#!/usr/bin/env python3
import requests
import sys
from concurrent.futures import ThreadPoolExecutor

TARGET_URL = "https://vulnerable-app.com/api/search"
PAYLOAD_FILE = "xss_payloads.txt"

def fuzz_parameter(payload):
    try:
        # Test GET parameter
        response = requests.get(
            TARGET_URL,
            params={"q": payload},
            timeout=5,
            verify=False
        )
        
        # Check for XSS reflection
        if payload in response.text:
            print(f"[+] Reflected XSS: {payload}")
            with open("vulnerabilities.txt", "a") as f:
                f.write(f"XSS: {payload}\n")
        
        # Check for SQL errors
        sql_errors = ["mysql", "syntax", "postgresql", "oracle", "sql"]
        if any(err in response.text.lower() for err in sql_errors):
            print(f"[+] SQL Error: {payload}")
            with open("vulnerabilities.txt", "a") as f:
                f.write(f"SQLi: {payload}\n")
        
        # Check for error messages
        if response.status_code == 500:
            print(f"[!] Server Error with: {payload}")
            with open("crashes.txt", "a") as f:
                f.write(f"{payload}\n")
                
    except Exception as e:
        print(f"[-] Error testing {payload}: {e}")

def main():
    # Load payloads
    with open(PAYLOAD_FILE) as f:
        payloads = [line.strip() for line in f if line.strip()]
    
    print(f"[*] Loaded {len(payloads)} payloads")
    print(f"[*] Target: {TARGET_URL}")
    
    # Parallel fuzzing
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fuzz_parameter, payloads)
    
    print("[*] Fuzzing complete")

if __name__ == "__main__":
    main()
```

### Step 6: File Format Fuzzing with Radamsa

**Install Radamsa:**
```bash
git clone https://gitlab.com/akihe/radamsa.git
cd radamsa
make
sudo make install
```

**Generate mutated files:**
```bash
# Single file mutation
radamsa sample.pdf > mutated1.pdf

# Batch generation
for i in {1..1000}; do
    radamsa sample.pdf > fuzz/mutated_$i.pdf
done

# Multiple seed files
cat seed1.png seed2.png seed3.png | radamsa -n 100 -o fuzz/mutated_%n.png
```

**Automated testing loop:**
```bash
#!/bin/bash
# fuzz_loop.sh

TARGET_APP="./pdf_viewer"
SEED_FILE="sample.pdf"
CRASH_DIR="crashes"

mkdir -p $CRASH_DIR

counter=0
while true; do
    counter=$((counter + 1))
    
    # Generate mutated file
    radamsa $SEED_FILE > /tmp/fuzz_input.pdf
    
    # Test with timeout
    timeout 5 $TARGET_APP /tmp/fuzz_input.pdf > /dev/null 2>&1
    exit_code=$?
    
    # Check for crash (segfault = 139)
    if [ $exit_code -eq 139 ] || [ $exit_code -eq 134 ]; then
        echo "[+] Crash found at iteration $counter"
        cp /tmp/fuzz_input.pdf $CRASH_DIR/crash_$counter.pdf
        
        # Get crash details
        gdb -batch -ex "run /tmp/fuzz_input.pdf" -ex "bt" $TARGET_APP 2>&1 | tee $CRASH_DIR/crash_$counter.txt
    fi
    
    # Progress
    if [ $((counter % 100)) -eq 0 ]; then
        echo "[*] Tested $counter inputs"
    fi
done
```

### Step 7: Automated Triage and Reporting

**Crash analysis script:**
```python
#!/usr/bin/env python3
# triage_crashes.py
import os
import subprocess
import hashlib
from collections import defaultdict

def get_crash_hash(binary, crash_file):
    """Get unique hash of crash stack trace"""
    try:
        # Run in GDB and extract backtrace
        gdb_cmd = [
            'gdb', '-batch',
            '-ex', f'run {crash_file}',
            '-ex', 'bt',
            binary
        ]
        
        result = subprocess.run(
            gdb_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Extract relevant stack frames
        bt_lines = [line for line in result.stdout.split('\n') if line.startswith('#')]
        
        # Hash the backtrace
        bt_hash = hashlib.md5('\n'.join(bt_lines).encode()).hexdigest()[:8]
        
        return bt_hash, '\n'.join(bt_lines)
        
    except Exception as e:
        return None, str(e)

def triage_crashes(binary, crash_dir):
    """Group crashes by unique stack trace"""
    unique_crashes = defaultdict(list)
    
    for crash_file in os.listdir(crash_dir):
        if not crash_file.endswith('.pdf'):  # Adjust extension
            continue
        
        crash_path = os.path.join(crash_dir, crash_file)
        
        print(f"[*] Analyzing {crash_file}...")
        crash_hash, backtrace = get_crash_hash(binary, crash_path)
        
        if crash_hash:
            unique_crashes[crash_hash].append({
                'file': crash_file,
                'backtrace': backtrace
            })
    
    # Generate report
    with open('triage_report.txt', 'w') as report:
        report.write(f"=== Crash Triage Report ===\n\n")
        report.write(f"Total crashes: {sum(len(v) for v in unique_crashes.values())}\n")
        report.write(f"Unique crashes: {len(unique_crashes)}\n\n")
        
        for crash_hash, crashes in unique_crashes.items():
            report.write(f"\n{'='*60}\n")
            report.write(f"Crash Hash: {crash_hash}\n")
            report.write(f"Occurrences: {len(crashes)}\n")
            report.write(f"Sample: {crashes[0]['file']}\n")
            report.write(f"\nBacktrace:\n{crashes[0]['backtrace']}\n")
    
    print(f"[+] Report saved to triage_report.txt")
    print(f"[+] Found {len(unique_crashes)} unique crashes")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <binary> <crash_dir>")
        sys.exit(1)
    
    triage_crashes(sys.argv[1], sys.argv[2])
```

### Step 8: Continuous Fuzzing Infrastructure

**Docker-based fuzzing setup:**
```dockerfile
# Dockerfile.fuzzer
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    python3 \
    python3-pip \
    gdb \
    vim

# Install AFL++
RUN git clone https://github.com/AFLplusplus/AFLplusplus /opt/aflplusplus && \
    cd /opt/aflplusplus && \
    make distrib && \
    make install

# Install libFuzzer/clang
RUN wget https://apt.llvm.org/llvm.sh && chmod +x llvm.sh && ./llvm.sh 15

WORKDIR /fuzzing
COPY target_binary /fuzzing/
COPY corpus /fuzzing/corpus/

CMD ["afl-fuzz", "-i", "corpus", "-o", "output", "-M", "fuzzer", "--", "./target_binary", "@@"]
```

**Run distributed fuzzing:**
```bash
# Build image
docker build -t fuzzer:latest -f Dockerfile.fuzzer .

# Run multiple fuzzing containers
for i in {1..8}; do
    docker run -d --name fuzzer_$i \
        -v $(pwd)/sync_dir:/fuzzing/output \
        fuzzer:latest \
        afl-fuzz -i corpus -o /fuzzing/output -S fuzzer_$i -- ./target @@
done

# Monitor
docker logs -f fuzzer_1
```

## Pitfalls

**Corpus quality**: Garbage inputs = garbage coverage. Start with valid samples.

**Timeout tuning**: Too long wastes time, too short misses slow bugs.

**Memory limits**: ASAN/MSAN increases memory usage significantly.

**Determinism**: Non-deterministic bugs are harder to reproduce.

**False positives**: Not all crashes are exploitable. Triage carefully.

## Verification

```bash
# Check if crashes are reproducible
./target_binary crash_file.pdf
echo $?  # Should crash consistently

# Verify with ASAN
export ASAN_OPTIONS=symbolize=1
./target_asan crash_file.pdf

# Check coverage
afl-showmap -o /dev/null -- ./target crash_file.pdf
# Higher edge count = better coverage
```

## OPSEC

- Fuzz in isolated VMs/containers
- Monitor resource usage (CPU/disk)
- Backup interesting crashes immediately
- Don't fuzz production systems
- Rate-limit API fuzzing

## References

- AFL++ documentation
- libFuzzer tutorial (LLVM)
- Google OSS-Fuzz project
- Fuzzing Book (fuzzingbook.org)
- Awesome Fuzzing (GitHub)
