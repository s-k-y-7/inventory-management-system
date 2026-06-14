from celery import shared_task
import time

@shared_task
def send_order_confirmation(order_id):
    """
    Simulates sending an order confirmation email asynchronously.
    """
    print(f"➔ [CELERY TASK STARTED] Gathering details for Order ID: {order_id}...")
    
    # Simulate network delay for rendering and sending an email
    time.sleep(3)
    
    print(f"➔ [CELERY TASK COMPLETED] Successfully sent email for Order ID: {order_id}!")
    return f"Confirmation sent for Order {order_id}"
