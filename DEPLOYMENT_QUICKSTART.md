# Deployment Quick Start

## Files Created

✅ **Infrastructure**
- `infrastructure/cloudformation-template.yaml` - AWS CloudFormation template

✅ **CI/CD**
- `.github/workflows/deploy-prod.yml` - GitHub Actions workflow

✅ **Scripts**
- `scripts/deploy.sh` - EC2 deployment script
- `scripts/get-ami.sh` - Helper to get AMI ID for your region

✅ **Documentation**
- `DEPLOYMENT.md` - Complete deployment guide

✅ **Code Updates**
- `src/config.py` - Updated to support SSM Parameter Store
- `requirements.txt` - Added boto3 for AWS SDK

## Next Steps

### 1. Set Up GitHub Secrets

Go to: GitHub Repository → Settings → Secrets and variables → Actions

Add these secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_KEY_PAIR_NAME`
- `AWS_SSH_PRIVATE_KEY`
- `OPENAI_API_KEY`

See `DEPLOYMENT.md` for detailed instructions.

### 2. Update AMI ID (if not using us-east-1)

```bash
# Get AMI for your region
bash scripts/get-ami.sh us-east-1

# Update ImageId in infrastructure/cloudformation-template.yaml
```

### 3. Deploy

Push to `main` branch or manually trigger the workflow:
- GitHub → Actions → Deploy to PROD → Run workflow

## Quick Commands

```bash
# Get AMI ID for region
bash scripts/get-ami.sh us-east-1

# Check deployment status
# (via GitHub Actions UI)

# SSH to instance (after deployment)
ssh -i chatbot-prod-key.pem ec2-user@<INSTANCE_IP>

# Check service status
sudo systemctl status chatbot-service

# View logs
sudo journalctl -u chatbot-service -f
```

## Important Notes

- The CloudFormation template uses AMI ID for **us-east-1** by default
- Update the AMI ID if deploying to a different region
- First deployment will create the CloudFormation stack
- Subsequent deployments will update the stack
- Database will be loaded automatically if `data/uber_data.csv` exists

For detailed information, see `DEPLOYMENT.md`.

