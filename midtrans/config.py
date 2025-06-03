import midtransclient

# Initialize the Midtrans client


def create_midtrans_client():
    # Use your Midtrans server key here
    server_key = 'YOUR_SERVER_KEY'
    is_sandbox = True  # True for sandbox, False for production

    snap = midtransclient.Snap(
        is_production=not is_sandbox,
        server_key=server_key
    )
    return snap
