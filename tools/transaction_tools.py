from langchain.tools import Tool

from midtrans.client import create_payment_link


def send_payment_link(id: str):
    """Send payment form link to user when they want to make a transaction"""
    print("Menuju ke link pembayaran/transaksi")
    payment_link = create_payment_link(id, 1_500_000)
    return f"Silakan klik link berikut untuk melakukan pembayaran: {payment_link}"


def send_bill_check_link(user_id: str, room_id: str):
    """Send bill checking form link to user when they want to check their bills"""
    print(user_id, room_id)

    print("Menuju ke link pengecekan tagihan")
    return "Silakan klik link berikut untuk mengecek tagihan Anda: https://payment-form.guesthouse.com/check-bills"


# Tools
transaction_tools = [
    Tool.from_function(
        name="send_payment_link",
        description="Kirim link form pembayaran ketika user ingin melakukan transaksi, pembayaran, atau bayar tagihan",
        func=send_payment_link,
    ),
    Tool.from_function(
        name="send_bill_check_link",
        description="Kirim link form pengecekan tagihan ketika user ingin cek tagihan, lihat tagihan, atau melihat status pembayaran",
        func=send_bill_check_link,
    ),
]
