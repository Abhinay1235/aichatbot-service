# Deployment Guide

## Overview

This guide covers deploying the AI Chatbot Service backend to AWS EC2 using CloudFormation and GitHub Actions.

## Architecture

- **Infrastructure**: AWS CloudFormation template creates EC2 instance, Security Groups, and IAM roles
- **CI/CD**: GitHub Actions workflow automates deployment on push to main branch
- **Secrets Management**: AWS Systems Manager (SSM) Parameter Store for sensitive data
- **Environment**: Single PROD environment

## Prerequisites

1. AWS Account with appropriate permissions
2. GitHub repository with Actions enabled
3. AWS CLI configured locally (for initial setup)

## GitHub Secrets Setup

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

### Required Secrets

1. **AWS_ACCESS_KEY_ID**
   - Description: AWS IAM user access key ID with CloudFormation, EC2, SSM permissions
   - How to create:
     - AWS Console → IAM → Users → Create user
     - Attach policies: `AmazonEC2FullAccess`, `CloudFormationFullAccess`, `IAMFullAccess`, `AmazonSSMFullAccess`
     - Create access key → Save the Access Key ID

2. **AWS_SECRET_ACCESS_KEY**
   - Description: AWS IAM user secret access key
   - Value: Secret from step 1

3. **AWS_KEY_PAIR_NAME**
   - Description: Name of EC2 Key Pair (must exist in your AWS region)
   - How to create:
     - AWS Console → EC2 → Key Pairs → Create key pair
     - Name: `chatbot-prod-key` (or your preferred name)
     - Save the .pem file securely

4. **AWS_SSH_PRIVATE_KEY**
   - Description: Private key content for SSH access to EC2
   - Value: Content of the .pem file from step 3
   - Copy the entire content including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`
   - Important: Include line breaks exactly as they appear in the file

5. **OPENAI_API_KEY**
   - Description: OpenAI API key for the chatbot service
   - Value: Your OpenAI API key (starts with `sk-`)

### Optional Configuration

6. **AWS_REGION** (if different from us-east-1)
   - Update the workflow file `env.AWS_REGION` in `.github/workflows/deploy-prod.yml`

## CloudFormation Stack Parameters

The stack uses these parameters (configurable in GitHub Actions workflow):
- `InstanceType`: t3.micro (free tier eligible)
- `KeyPairName`: From GitHub secret `AWS_KEY_PAIR_NAME`
- `Environment`: PROD

## Initial Setup

### 1. Get AMI ID for Your Region

Update the AMI ID in `infrastructure/cloudformation-template.yaml`:

```bash
# Run the helper script
bash scripts/get-ami.sh us-east-1

# Or manually query
aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-*-x86_64" "Name=state,Values=available" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --region us-east-1 \
  --output text
```

Update `ImageId` in the CloudFormation template with the result.

### 2. Create EC2 Key Pair (if not exists)

```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name chatbot-prod-key \
  --query 'KeyMaterial' \
  --output text > chatbot-prod-key.pem

# Set permissions
chmod 400 chatbot-prod-key.pem

# Add the key pair name to GitHub secrets as AWS_KEY_PAIR_NAME
# Add the .pem file content to GitHub secrets as AWS_SSH_PRIVATE_KEY
```

## Deployment Process

### Automatic Deployment

1. **Push to main branch** → Automatic deployment triggers
2. Monitor in GitHub Actions tab

### Manual Deployment

1. Go to GitHub repository → **Actions** tab
2. Select **Deploy to PROD** workflow
3. Click **Run workflow** → Select branch → **Run workflow**

### Deployment Steps

The GitHub Actions workflow performs:

1. ✅ Checkout code
2. ✅ Configure AWS credentials
3. ✅ Create/Update CloudFormation stack
4. ✅ Get EC2 instance IP
5. ✅ Store OpenAI API key in SSM Parameter Store
6. ✅ Wait for EC2 instance to be ready
7. ✅ Setup SSH connection
8. ✅ Deploy application to EC2
9. ✅ Health check
10. ✅ Deployment summary

## Post-Deployment

### Get Instance Information

1. From GitHub Actions summary (after deployment completes)
2. From AWS Console → CloudFormation → Stack Outputs
3. From AWS CLI:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name chatbot-prod-infrastructure \
     --query 'Stacks[0].Outputs' \
     --output table
   ```

### Test the Deployment

```bash
# Health check
curl http://<INSTANCE_IP>:8000/health

# Root endpoint
curl http://<INSTANCE_IP>:8000/

# API Documentation
open http://<INSTANCE_IP>:8000/docs
```

### Access EC2 Instance

```bash
# SSH to instance
ssh -i chatbot-prod-key.pem ec2-user@<INSTANCE_IP>

# Check service status
sudo systemctl status chatbot-service

# View service logs
sudo journalctl -u chatbot-service -f

# View recent logs
sudo journalctl -u chatbot-service -n 100
```

## Monitoring

### Service Logs

```bash
# Real-time logs
sudo journalctl -u chatbot-service -f

# Last 50 lines
sudo journalctl -u chatbot-service -n 50

# Logs since boot
sudo journalctl -u chatbot-service -b
```

### Application Health

- Health endpoint: `http://<INSTANCE_IP>:8000/health`
- API docs: `http://<INSTANCE_IP>:8000/docs`

### AWS CloudWatch

- EC2 metrics available in CloudWatch console
- IAM role includes CloudWatchAgentServerPolicy for enhanced monitoring

## Troubleshooting

### Stack Creation/Update Fails

**Issue**: CloudFormation stack creation fails
- **Check**: IAM permissions for GitHub Actions user
- **Verify**: Key pair exists in the region
- **Check**: CloudFormation logs in AWS Console

### Deployment Fails - SSH Connection

**Issue**: Cannot connect to EC2 instance
- **Check**: Security group allows SSH (port 22) from GitHub Actions IPs
- **Verify**: SSH key format in GitHub secrets (must include line breaks)
- **Check**: Instance is running (not in pending state)

### Service Won't Start

**Issue**: Systemd service fails to start
- **SSH to instance**: `ssh -i chatbot-prod-key.pem ec2-user@<INSTANCE_IP>`
- **Check logs**: `sudo journalctl -u chatbot-service -n 50`
- **Verify**: Database exists: `ls -la /opt/chatbot-service/database/`
- **Check**: Python dependencies: `cd /opt/chatbot-service && source venv/bin/activate && pip list`
- **Test manually**: `cd /opt/chatbot-service && source venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8000`

### Database Issues

**Issue**: Database not found or corrupted
- **Check**: Database file exists: `ls -la /opt/chatbot-service/database/chatbot.db`
- **Reload data**: 
  ```bash
  cd /opt/chatbot-service
  source venv/bin/activate
  python scripts/load_data.py data/uber_data.csv
  ```

### OpenAI API Key Issues

**Issue**: API key not found
- **Check**: SSM parameter exists: 
  ```bash
  aws ssm get-parameter --name /chatbot/prod/OPENAI_API_KEY --with-decryption
  ```
- **Verify**: IAM role has SSM read permissions
- **Check**: Environment variable in systemd service:
  ```bash
  sudo systemctl show chatbot-service | grep OPENAI_API_KEY
  ```

### Health Check Fails

**Issue**: Health check endpoint returns error
- **Wait**: Service may need more time to start (30-60 seconds)
- **Check**: Service is running: `sudo systemctl status chatbot-service`
- **Verify**: Port 8000 is accessible: `curl localhost:8000/health`
- **Check**: Security group allows traffic on port 8000

## Cost Estimation

- **EC2 t3.micro**: $0/month (first 12 months free tier), then ~$7.50/month
- **EBS Storage (8 GB)**: $0/month (free tier covers 30 GB), then ~$0.80/month
- **Data Transfer**: Minimal cost for portfolio use (~$0.10/month)
- **SSM Parameter Store**: $0.05/month per parameter (free tier: 10,000 parameters)
- **CloudFormation**: Free

**Total Estimated Cost**: 
- First 12 months: ~$0.15/month
- After free tier: ~$8.50/month

## Maintenance

### Update Application

Simply push to `main` branch - GitHub Actions will automatically deploy.

### Update Infrastructure

Modify `infrastructure/cloudformation-template.yaml` and push to main. CloudFormation will update the stack.

### Scale Up

To use a larger instance:
1. Update `InstanceType` parameter in GitHub Actions workflow (e.g., `t3.small`)
2. Push to main or manually trigger workflow

### Backup Database

```bash
# SSH to instance
ssh -i chatbot-prod-key.pem ec2-user@<INSTANCE_IP>

# Copy database
sudo cp /opt/chatbot-service/database/chatbot.db /tmp/chatbot-backup-$(date +%Y%m%d).db

# Download to local machine
scp -i chatbot-prod-key.pem ec2-user@<INSTANCE_IP>:/tmp/chatbot-backup-*.db ./
```

## Cleanup

To delete all resources:

```bash
aws cloudformation delete-stack \
  --stack-name chatbot-prod-infrastructure \
  --region us-east-1
```

**Note**: This will delete the EC2 instance and all data. Make sure to backup the database first if needed.

