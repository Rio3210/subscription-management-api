# Subscription Management API

A RESTful API for managing user subscriptions with optimized database queries and performance considerations.

## Features

- User registration and authentication
- Subscription plan management
- User subscription handling (subscribe, upgrade, cancel)
- Optimized database queries with proper indexing
- Performance monitoring and analysis

## Setup Instructions

### Using Docker

1. Build the Docker image:
```bash
docker build -t subscription-api .
```

2. Run the container:
```bash
docker run -p 5000:5000 subscription-api
```

3. Access the API:
   - The API will be available at `http://localhost:5000`
   - Use the Swagger documentation at `http://localhost:5000/api/docs`

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize and set up the database:
```bash
# Initialize the database migrations
flask --app "app:create_app('development')" db init

# Create the initial migration
flask --app "app:create_app('development')" db migrate -m "Initial migration"

# Apply the migrations to create/update the database schema
flask --app "app:create_app('development')" db upgrade
```

4. Run the application:
```bash
python run.py
```

## API Documentation

### Authentication Endpoints
- POST /auth/register - Register a new user
- POST /auth/login - Login user

### Subscription Plan Endpoints
- GET /plans - List all subscription plans
- POST /plans - Create a new subscription plan (admin only)

### Subscription Endpoints
- POST /subscriptions - Subscribe to a plan
- PUT /subscriptions/<subscription_id> - Update subscription
- DELETE /subscriptions/<subscription_id> - Cancel subscription
- GET /subscriptions - List user's subscriptions


## Database Optimization

The API includes several optimizations:
- Proper indexing on frequently queried columns
- Optimized raw SQL queries where needed
- Efficient subscription status tracking
- Caching strategies for frequently accessed data

## Testing

Run tests using pytest:(not implemented)
```bash
pytest
``` 