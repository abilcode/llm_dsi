from langchain.tools import StructuredTool
from midtrans.client import create_payment_link

def send_payment_link(booking_id: str, room_price: float) -> str:
    print("Menuju ke link pembayaran/transaksi")
    payment_link = create_payment_link(booking_id=booking_id, price=room_price)
    return f"Silakan klik link berikut untuk melakukan pembayaran: {payment_link}"

def send_bill_check_link(user_id: str) -> str:
    print("Menuju ke link pengecekan tagihan")
    return "Silakan klik link berikut untuk mengecek tagihan Anda: https://payment-form.guesthouse.com/check-bills"

transaction_tools = [
    StructuredTool.from_function(
        func=send_payment_link,
        name="send_payment_link",
        description=(
            "Kirim link form pembayaran ketika user ingin melakukan transaksi, pembayaran, atau bayar tagihan.\n"
            "Gunakan format argumen sebagai berikut:\n"
            "- booking_id (str): gabungkan ID dan room id dengan snake_case, contoh: '23232_1' 23232 is telegram ID or ID and room ID is room ID.\n"
            "- room_price (float): harga dalam Rupiah, contoh: 2_000_000. Ini adalah harga room price yang diperoleh dari DatabaseAgent. Tidak boleh 0, harus sesuai dengan data yang ada. Tidak boleh ngarang."
        ),
    ),
    StructuredTool.from_function(
        func=send_bill_check_link,
        name="send_bill_check_link",
        description="Kirim link form pengecekan tagihan ketika user ingin cek tagihan, lihat tagihan, atau melihat status pembayaran",
    ),
]