import requests

def get_html_from_url(url):
    response = requests.get(url)
    html = response.text
    return html