# HTTPS Setup for Backend API

## Problem

The UI is served over HTTPS (Amplify) but the backend API uses HTTP. Modern browsers block mixed content (HTTPS page calling HTTP API).

## Solution Options

### Option 1: CloudFront Distribution (Recommended for Minimal Cost)

CloudFront can terminate HTTPS and forward to HTTP backend. **First 1TB free per month** (perfect for portfolio).

#### Steps:

1. **Create CloudFront Distribution via AWS Console:**

   ```
   AWS Console → CloudFront → Create Distribution
   ```

2. **Origin Settings:**
   - **Origin Domain**: `44.203.107.110` (your EC2 IP)
   - **Origin Protocol**: HTTP
   - **Origin Port**: 8000
   - **Origin Path**: (leave empty)

3. **Default Cache Behavior:**
   - **Viewer Protocol Policy**: Redirect HTTP to HTTPS
   - **Allowed HTTP Methods**: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
   - **Cache Policy**: CachingDisabled (for API endpoints)

4. **Distribution Settings:**
   - **Price Class**: Use only North America and Europe (cheaper)
   - **SSL Certificate**: Default CloudFront Certificate (*.cloudfront.net)
   - **Custom SSL Certificate**: (Optional) Use ACM certificate for custom domain

5. **Create Distribution** (takes 5-10 minutes)

6. **Get CloudFront URL:**
   - Format: `https://d1234567890.cloudfront.net`
   - Update UI API endpoint to this URL

#### Cost: **FREE** (for portfolio use - first 1TB free/month)

---

### Option 2: Application Load Balancer + ACM Certificate

Adds SSL termination at ALB. Requires subnets and ACM certificate.

#### Cost: ~$16/month (ALB) + $0 (ACM certificate)

#### Steps:

1. **Get Default VPC Subnets:**
   ```bash
   aws ec2 describe-subnets --filters "Name=vpc-id,Values=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)" --query 'Subnets[*].[SubnetId,AvailabilityZone]' --output table
   ```

2. **Request ACM Certificate:**
   - Go to AWS Certificate Manager
   - Request public certificate
   - Use domain or use ALB DNS name

3. **Update CloudFormation** to add ALB (see updated template)

---

### Option 3: Quick Fix - Use HTTP for Now (Testing Only)

For portfolio demonstration, you can:
1. Open browser settings and allow insecure content (not recommended)
2. Or document this as a known limitation

---

## Recommended: CloudFront Setup

Here's the detailed CloudFront setup:

### Create CloudFront Distribution

**Via AWS Console:**

1. Go to CloudFront Console
2. Click "Create Distribution"
3. Configure:

   **Origin:**
   - Origin domain: `44.203.107.110`
   - Origin path: (empty)
   - Name: `chatbot-api-prod`
   - Origin protocol policy: HTTP Only
   - HTTP port: 8000
   - Origin keepalive timeout: 5
   - Origin request timeout: 30

   **Default Cache Behavior:**
   - Viewer protocol policy: **Redirect HTTP to HTTPS**
   - Allowed HTTP methods: All
   - Cache policy: **CachingDisabled** (important for API)
   - Origin request policy: **CORS-S3Origin** or **AllViewer**
   - Response headers policy: Add CORS headers if needed

   **Distribution Settings:**
   - Price class: Use only North America and Europe
   - SSL certificate: Default CloudFront Certificate (*.cloudfront.net)
   - Custom domain: (optional, requires domain and ACM cert)

4. Click "Create Distribution"
5. Wait 5-10 minutes for deployment

### Update UI to Use CloudFront URL

After CloudFront is created, you'll get a URL like:
```
https://d1234567890.cloudfront.net
```

Update the UI environment variable in Amplify:
```
VITE_API_URL = https://d1234567890.cloudfront.net
```

Or update `src/utils/constants.ts`:
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://d1234567890.cloudfront.net'
```

### Update Backend CORS

Update `src/main.py` CORS to include CloudFront domain:
```python
allowed_origins = [
    "https://main.d2hgspiyjkz5p5.amplifyapp.com",  # Amplify UI
    "https://d1234567890.cloudfront.net",  # CloudFront API (if needed)
    "http://localhost:3000",  # Local dev
]
```

---

## Cost Comparison

| Solution | Monthly Cost | Complexity |
|----------|--------------|------------|
| CloudFront | $0 (first 1TB free) | Low |
| Application Load Balancer | ~$16 | Medium |
| Custom Domain + SSL | ~$12/year domain | High |

**Recommendation**: Use CloudFront - it's free for your use case and simple to set up.

---

## Quick Setup Script (CloudFront via CLI)

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json

# Get distribution URL
aws cloudfront list-distributions \
  --query 'DistributionList.Items[?Comment==`chatbot-api-prod`].DomainName' \
  --output text
```

---

## After Setup

1. ✅ CloudFront distribution created
2. ✅ Update UI API endpoint to CloudFront URL
3. ✅ Update backend CORS if needed
4. ✅ Test from Amplify UI - should work over HTTPS

The mixed content error will be resolved because CloudFront provides HTTPS termination.

