from langchain.tools import Tool

def send_payment_link(user_request: str):
    """Send payment form link to user when they want to make a transaction"""
    print("Menuju ke link pembayaran/transaksi")
    return "Silakan klik link berikut untuk melakukan pembayaran: https://payment-form.guesthouse.com/payment"

def send_bill_check_link(user_request: str):
    """Send bill checking form link to user when they want to check their bills"""
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