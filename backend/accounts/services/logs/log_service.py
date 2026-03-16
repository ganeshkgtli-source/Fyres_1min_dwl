from accounts.models import DownloadLog


def save_log(file_name, trade_date, week_day, status):

    DownloadLog.objects.update_or_create(

        file_name=file_name,

        defaults={
            "trade_date": trade_date,
            "week_day": week_day,
            "status": status
        }

    )