from datetime import datetime, timedelta

def get_latest_n_date_strings(n=1):
    date_strings = []
    today = datetime.now().date()
    for i in range(n, -1, -1):
        date = today - timedelta(days=i)
        date_string = date.strftime('%Y-%m-%d')
        date_strings.append(date_string)
    return date_strings

date_strings = get_latest_n_date_strings()
print(date_strings)
