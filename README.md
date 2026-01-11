# AI Chatbot Service

AI-powered chatbot backend service for analyzing Uber trip data. Built with FastAPI, SQLite, and OpenAI GPT-3.5-turbo.

## 🌐 Production API

**API Endpoint:** `https://ai-chatbot-service.abhinaykumar.com`

- **Health Check:** https://ai-chatbot-service.abhinaykumar.com/health
- **API Documentation:** https://ai-chatbot-service.abhinaykumar.com/docs

## Overview

This service provides:
- **Natural language queries** to analyze car rides data for a particular period
- **Conversation context persistence** - remembers previous questions in a session
- **Cost-efficient architecture** - SQLite database, GPT-3.5-turbo model
- **RESTful API** for chatbot interactions
- **Production deployment** on AWS EC2 with HTTPS via Nginx
- **Automated CI/CD** via GitHub Actions

## Features

- 📊 Analyze Car rides data through natural language questions
- 💬 Maintain conversation context across multiple questions
- 💰 Cost-optimized (SQLite + GPT-3.5-turbo)
- 🚀 Fast API built with FastAPI
- 📝 Auto-generated API documentation (Swagger UI)
- 🔒 HTTPS enabled with Let's Encrypt SSL certificate
- ☁️ AWS infrastructure managed via CloudFormation
- 🔄 Automated deployments via GitHub Actions
- 🔐 Secure secrets management via AWS SSM Parameter Store

## Getting Started

For local development setup, see the [QUICK_SETUP.md](QUICK_SETUP.md) guide.

**Quick Overview:**
1. Create virtual environment: `python3 -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env` file with your OpenAI API key
4. Load data: `python scripts/load_data.py data/uber_data.csv`
5. Start server: `uvicorn src.main:app --reload`

For detailed instructions, troubleshooting, and additional configuration options, see [QUICK_SETUP.md](QUICK_SETUP.md) or [SETUP.md](SETUP.md).

## Project Structure

```
aichatbot-service/
├── src/                    # Source code
│   ├── main.py             # FastAPI application with CORS
│   ├── config.py           # Configuration
│   ├── database/           # Database models and session
│   ├── services/           # Business logic
│   ├── api/                # API routes
│   └── utils/              # Utilities
├── infrastructure/         # AWS infrastructure as code
│   └── cloudformation-template.yaml  # CloudFormation template
├── .github/                # GitHub Actions workflows
│   └── workflows/
│       └── deploy-prod.yml # Automated deployment pipeline
├── nginx/                  # Nginx configuration
│   └── chatbot-api.conf    # Reverse proxy config
├── scripts/                # Utility scripts
│   ├── deploy.sh           # EC2 deployment script
│   └── setup-nginx-ssl.sh  # Nginx SSL setup script
├── data/                   # CSV data files
├── database/               # SQLite database (created automatically)
└── tests/                  # Test files
```

## API Endpoints

- `POST /api/chat` - Send a message to the chatbot
- `GET /api/sessions` - List all sessions (with optional `?limit=100` query param)
- `GET /api/sessions/{session_id}` - Get conversation history for a session
- `DELETE /api/sessions/{session_id}` - Delete a session
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API information


## Deployment

The service is deployed to **AWS EC2** with automated CI/CD via **GitHub Actions**.

### Infrastructure

- **Cloud Provider:** AWS
- **Compute:** EC2 t3.micro instance (free tier eligible)
- **Infrastructure as Code:** AWS CloudFormation
- **CI/CD:** GitHub Actions
- **Reverse Proxy:** Nginx with Let's Encrypt SSL
- **Secrets Management:** AWS Systems Manager (SSM) Parameter Store

### Deployment Guides

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide with AWS setup
- **[NGINX_SSL_SETUP.md](NGINX_SSL_SETUP.md)** - Nginx and SSL certificate setup
- **[SETUP.md](SETUP.md)** - Local development setup

### Quick Deployment Overview

1. **Infrastructure:** CloudFormation creates EC2 instance, Security Groups, and IAM roles
2. **CI/CD:** GitHub Actions automatically deploys on push to main branch
3. **Secrets:** OpenAI API key stored in SSM Parameter Store
4. **SSL:** Nginx configured with Let's Encrypt for HTTPS
5. **Domain:** API accessible at `https://ai-chatbot-service.abhinaykumar.com`

### Environment Variables

**Local Development:**
Create a `.env` file with:
```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
DATABASE_URL=sqlite:///./database/chatbot.db
```

**Production:**
- OpenAI API key is stored in AWS SSM Parameter Store at `/chatbot/PROD/OPENAI_API_KEY`
- Retrieved at runtime by the application via AWS SDK
- No secrets stored in code or environment files


## Development

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the complete development plan.

## Technology Stack

### Backend
- **Framework:** FastAPI
- **Database:** SQLite
- **AI/LLM:** OpenAI GPT-3.5-turbo
- **Data Processing:** pandas, numpy
- **ORM:** SQLAlchemy
- **Server:** Uvicorn (ASGI)

### Infrastructure & DevOps
- **Cloud:** AWS (EC2, CloudFormation, SSM)
- **CI/CD:** GitHub Actions
- **Reverse Proxy:** Nginx
- **SSL/TLS:** Let's Encrypt (Certbot)
- **Process Manager:** systemd
- **Secrets:** AWS Systems Manager Parameter Store

## Cost Optimization

### Infrastructure Costs
- **EC2 t3.micro:** Free (first 12 months AWS free tier), then ~$7.50/month
- **EBS Storage (8 GB):** Free (free tier covers 30 GB)
- **Data Transfer:** Minimal (~$0.10/month for portfolio use)
- **SSM Parameter Store:** $0.05/month per parameter (free tier: 10,000 parameters)
- **CloudFormation:** Free
- **Nginx & Certbot:** Free and open-source

### API Costs
- **SQLite:** Free (file-based database, no hosting costs)
- **GPT-3.5-turbo:** ~$0.0015/1K tokens (vs GPT-4's ~$0.03/1K tokens)
- Context window limiting
- Query caching

**Total Estimated Monthly Cost:**
- **First 12 months:** ~$0.15/month (mostly API usage)
- **After free tier:** ~$8.50/month (infrastructure) + API usage (~$5-20/month)

## Data Source & Credits

The Car Rides data used in this project is sourced from a public dataset on Kaggle:

**Dataset:** [Ola and Uber Ride Booking and Cancellation Data](https://www.kaggle.com/datasets/hetmengar/ola-and-uber-ride-booking-and-cancellation-data)

This dataset contains ride booking and cancellation data for dates from July 01, 2024 to July 31, 2024, used for demonstration and analysis purposes in this portfolio project.

## Additional Resources

- **[QUICK_SETUP.md](QUICK_SETUP.md)** - Quick setup guide for local development
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment instructions
- **[NGINX_SSL_SETUP.md](NGINX_SSL_SETUP.md)** - Nginx and SSL setup guide
- **[SETUP.md](SETUP.md)** - Comprehensive local development setup
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - API usage examples
- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Development roadmap

## License

Personal portfolio project.

