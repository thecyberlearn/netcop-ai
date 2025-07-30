# NetCop AI Agent - Django Web App

A production-ready Django web application with user authentication, Stripe payments, wallet system, and n8n workflow integration.

## Features

- **User Authentication**: Email-based signup/login with token authentication
- **Wallet System**: Stripe Checkout integration for wallet top-ups
- **Workflow Integration**: Secure n8n webhook triggering with automatic fee deduction
- **Admin Interface**: Django Admin for monitoring users, transactions, and usage
- **Security**: Rate limiting, authentication middleware, CSRF protection

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/profile/` - Get user profile

### Wallet
- `POST /api/wallet/top-up/` - Create Stripe Checkout session
- `GET /api/wallet/transactions/` - Get transaction history
- `POST /api/wallet/webhook/stripe/` - Stripe webhook handler

### Workflows
- `POST /api/workflows/trigger/<workflow_name>/` - Trigger n8n workflow
- `GET /api/workflows/history/` - Get workflow usage history

## Setup

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd netcop_ai_agent
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Database setup:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## Environment Variables

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1

STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook
N8N_API_KEY=your-n8n-api-key

WORKFLOW_FEE=0.10
```

## Deployment

### Heroku
1. Create a new Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy using Git:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Render
1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Deploy automatically on git push

## Models

- **User**: Custom user model with email authentication and wallet balance
- **WalletTransaction**: Track deposits, withdrawals, and fees
- **WorkflowUsage**: Log n8n workflow triggers and associated costs

## Security Features

- Rate limiting (10 requests per minute for workflow triggers)
- CSRF protection
- Token-based authentication
- Stripe webhook signature verification
- Environment-based configuration