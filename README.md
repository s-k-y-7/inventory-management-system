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

## Implementation Notes
- **Data Consistency:** Uses `transaction.atomic()` during order creation to ensure data integrity.
- **Queries:** Uses `select_related` and `annotate` to optimize database queries.
- **Ports:** PostgreSQL and Redis host ports are intentionally not exposed in `docker-compose.yml` to prevent conflicts with local services.
