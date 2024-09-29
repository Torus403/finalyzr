# Finalyzr: Portfolio Analysis API

**Documentation**: [api.finalyzr.app/docs](https://api.finalyzr.app/docs)

**Source Code**: [github.com/Torus403/finalyzr](https://github.com/Torus403/finalyzr)

---

Finalyzr is a modern API built with FastAPI for comprehensive portfolio analysis. It provides endpoints for managing portfolios, trades, cash actions, and generating various financial metrics.

## Key Features

- **Portfolio Management**: Create, update, and delete portfolios.
- **Trade Management**: Upload trades and calculate key metrics such as Sharpe ratio and benchmark comparisons.
- **Cash Actions**: Manage deposits and withdrawals and track cash flow in portfolios.
- **Financial Metrics**: Analyze portfolio performance over time with various risk metrics.
- **API-First Design**: Automatically generated interactive API documentation using OpenAPI and ReDoc.
- **User Authentication**: Secure user management with OAuth2 and JWT tokens.

## Requirements

- **Python 3.8+**
- **FastAPI**
- **SQLAlchemy**
- **Pydantic**

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Torus403/finalyzr.git
    cd finalyzr
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file at the root of your project to store necessary environment variables like database credentials and secret keys. Example:
    ```env
    DATABASE_URL=sqlite:///./finalyzr.db
    SECRET_KEY=your_secret_key
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5. **Run database migrations**:
    ```bash
    alembic upgrade head
    ```

6. **Start the development server**:
    ```bash
    uvicorn app.main:app --reload
    ```

## API Usage

### Example Endpoints

1. **Create a Portfolio**
    ```bash
    POST /portfolios/
    ```

    Body:
    ```json
    {
        "name": "My Portfolio",
        "description": "A description of the portfolio."
    }
    ```

2. **Add a Trade**
    ```bash
    POST /portfolios/{portfolio_id}/trades/
    ```

    Body:
    ```json
    {
        "ticker": "AAPL",
        "action": "buy",
        "price": 150.0,
        "quantity": 10,
        "execution_timestamp": "2023-09-01T12:00:00Z"
    }
    ```

3. **Get Portfolio Metrics**
    ```bash
    GET /portfolios/{portfolio_id}/metrics/
    ```

    Response:
    ```json
    {
        "sharpe_ratio": 1.5,
        "annual_return": 0.12,
        "volatility": 0.05
    }
    ```

For more detailed usage and endpoint documentation, visit the interactive API docs at: [api.finalyzr.app/docs](https://api.finalyzr.app/docs).

## Running Tests

To run the tests, use `pytest`:

```bash
pytest
```

## Contribution Guidelines

1. Fork the repository.
2. Create a new branch for your feature
3. Submit a pull request with a clear description of the changes

## License

Finalyzr is licensed under the MIT License. See LICENSE for more information.