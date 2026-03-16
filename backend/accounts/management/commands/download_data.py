from django.core.management.base import BaseCommand
from accounts.services.history_service import download_1min_data

from accounts.services.fyers_client import get_fyers_client


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        client_id = get_fyers_client

        download_1min_data(client_id)