from datetime import date
from accounts.models import AccessToken

def get_today_access_token(client_id):

    try:
        token_obj = AccessToken.objects.get(
            client_id=client_id,
            token_date=date.today()
        )

        return token_obj.get_token()

    except AccessToken.DoesNotExist:
        raise Exception("Access token not found for today")