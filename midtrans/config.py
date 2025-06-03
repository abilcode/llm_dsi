import os
from dotenv import load_dotenv
import midtransclient

load_dotenv()


def create_midtrans_client():
    server_key = os.getenv("MIDTRANS_SERVER_KEY", "")
    is_sandbox = True

    snap = midtransclient.Snap(
        is_production=not is_sandbox,
        server_key=server_key
    )
    return snap
