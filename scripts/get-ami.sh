#!/bin/bash
# Get latest Amazon Linux 2023 AMI ID for your region
# Usage: ./get-ami.sh [region]
# Example: ./get-ami.sh us-east-1

REGION=${1:-us-east-1}

echo "Fetching latest Amazon Linux 2023 AMI ID for region: $REGION"
echo ""

AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-*-x86_64" "Name=state,Values=available" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --region $REGION \
  --output text 2>/dev/null)

if [ -z "$AMI_ID" ] || [ "$AMI_ID" == "None" ]; then
  echo "❌ Error: Could not find AMI. Check AWS CLI configuration and region."
  exit 1
fi

echo "✅ Found AMI: $AMI_ID"
echo ""
echo "Update this AMI ID in infrastructure/cloudformation-template.yaml:"
echo "  ImageId: $AMI_ID"
echo ""

# Also show AMI details
echo "AMI Details:"
aws ec2 describe-images \
  --image-ids $AMI_ID \
  --region $REGION \
  --query 'Images[0].[Name, ImageId, CreationDate]' \
  --output table

