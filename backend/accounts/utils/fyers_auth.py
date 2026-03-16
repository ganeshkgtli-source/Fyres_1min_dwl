from fyers_apiv3 import fyersModel


def generate_fyers_token(user, auth_code):

    session = fyersModel.SessionModel(
        client_id=user.client_id,
        secret_key=user.secret_key,
        redirect_uri="http://127.0.0.1:8000/api/fyers-callback/",
        response_type="code",
        grant_type="authorization_code"
    )

    session.set_token(auth_code)

    response = session.generate_token()

    return response.get("access_token")