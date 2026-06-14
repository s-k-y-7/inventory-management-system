# Inventory Management Backend

A backend module for an inventory management system built with Django and Django REST Framework. The project is containerized using Docker and uses Redis for caching and Celery for asynchronous tasks.

## Features
- **Database:** PostgreSQL schema for Products, Categories, Stores, Inventory, and Orders. Includes unique constraints to prevent inventory duplication.
- **Order Processing:** Transaction-safe endpoint (`select_for_update`) for order creation and inventory deduction.
- **Inventory & Search:** Endpoints for inventory listing, product search (with filtering/sorting), and autocomplete.
- **Caching:** Redis caching for inventory listings, with cache invalidation upon order creation.
- **Async Tasks:** Celery worker for handling background tasks (e.g., simulating order confirmation emails).
- **Docker:** Configured with `docker-compose` for local development.

## Prerequisites
- Docker Desktop installed and running.

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd inventory-management-system
   ```

2. **Run the application**
   Use Docker Compose to build and start the database, Redis, web server, and Celery worker:
   ```bash
   docker-compose up --build
   ```
   The API will be available at `http://localhost:8000`.

3. **Generate Seed Data**
   While the containers are running, open a new terminal window to populate the database with test data (Products, Stores, and Inventory):
   ```bash
   docker-compose exec web python manage.py seed_data
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/orders/` | Create an order. Requires `store_id` and `items`. Deducts inventory and triggers async confirmation task. |
| `GET` | `/stores/<store_id>/inventory/` | Get a store's inventory. Cached in Redis for 15 minutes. |
| `GET` | `/stores/<store_id>/orders/` | Get all orders placed at a specific store. |
| `GET` | `/api/search/products/` | Search global products (e.g., `?q=laptop&min_price=100&sort=price`). |
| `GET` | `/api/search/suggest/` | Autocomplete search for products (e.g., `?q=Pho`). |

### Testing the APIs (Example Requests)
Because there is no frontend, you can use the built-in Django REST Framework Browsable API (by clicking the links in your browser), Postman, or cURL to test the endpoints.

**1. Find a valid product to order:**
First, hit the search API to find a product and see which store has it in stock:
`GET http://localhost:8000/api/search/products/?q=a`

**2. Create an Order:**
Navigate to `http://localhost:8000/orders/` in your browser. In the "Content" box at the bottom, submit a JSON payload using the `store_id` and `product_id` you found above. Example payload:
```json
{
    "store_id": 1,
    "items": [
        {
            "product_id": 5,
            "quantity_requested": 2
        }
    ]
}
```
*(Note: Check the terminal running `docker-compose` to see the Celery background task execute in real-time upon a successful order!)*

**3. Check Cache Invalidation:**
Visit `http://localhost:8000/stores/1/inventory/` before and after placing an order. The first load caches the data in Redis; after an order is successfully placed, the cache is instantly invalidated and fetches the newly deducted inventory.

## Approach & Assumptions

**Approach:**
- **Data Consistency:** Used `transaction.atomic()` and `select_for_update()` during order creation to ensure data integrity and prevent race conditions.
- **Queries:** Used `select_related` and `annotate` to optimize database queries and eliminate N+1 issues.
- **Ports:** PostgreSQL and Redis host ports are intentionally not exposed in `docker-compose.yml` to prevent conflicts with local services. The containers communicate internally.

**Assumptions:**
- **Partial Fulfillment:** It is assumed that orders must be fulfilled entirely. If any product in an order lacks sufficient stock, the entire order is rejected rather than partially fulfilled.
- **Seed Data:** The `seed_data` script assumes a completely fresh database and randomly generates names/prices.
- **Cache Lifecycle:** It is assumed that inventory only changes via the `POST /orders/` endpoint, so cache invalidation is strictly tied to successful order creation.
