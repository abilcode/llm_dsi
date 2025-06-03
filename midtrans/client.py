from midtrans.config import create_midtrans_client


def create_payment_link(booking_id: str, price: int) -> str:
    snap = create_midtrans_client()

    transaction_params = {
        "transaction_details": {
            "order_id": booking_id,
            "gross_amount": price,
        },
        "item_details": [
            {
                "id": booking_id,
                "price": price,
                "quantity": 1,
                "name": f"Kamar {booking_id}"
            }
        ],
        "customer_details": {
        },
    }

    try:
        transaction_response = snap.create_transaction(transaction_params)
        payment_url = transaction_response['redirect_url']
        return payment_url
    except Exception as e:
        print(f"Error creating Midtrans transaction: {e}")
        return "Failed"
