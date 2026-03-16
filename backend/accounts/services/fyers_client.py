from fyers_apiv3 import fyersModel
from accounts.utils.token_manager import get_today_access_token

def get_fyers_client(client_id):

    access_token = get_today_access_token(client_id)

    fyers = fyersModel.FyersModel(
        client_id=client_id,
        token=access_token,
        is_async=False,
        log_path=""
    )

    return fyers