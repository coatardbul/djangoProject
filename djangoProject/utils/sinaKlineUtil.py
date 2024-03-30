
import json

import requests


def get_stock_minute_info(code):
    headers = set_headers_list(code)
    code_url = get_code_url(code)

    try:
        response = requests.get(
            f"https://quotes.sina.cn/cn/api/openapi.php/CN_MinlineService.getMinlineData?symbol={code_url}",
            headers=headers, proxies=get_proxy_flag())
        return response.text
    except requests.ConnectTimeout:
        return None


def get_code_url(code):
    if code.startswith("00") or code.startswith("30"):
        return f"sz{code}"
    else:
        return f"sh{code}"


def set_headers_list(code_url):
    # Replace 'get_head' and 'get_proxy_flag' with the actual methods to set headers and proxies.
    headers = {"Referer": f"https://finance.sina.com.cn/realstock/company/{code_url}/nc.shtml"}
    return headers


def get_proxy_flag():
    # You need to replace this with your actual method of obtaining proxy settings.
    # If you don't use a proxy, you can simply return None or an empty dictionary.
    return {}
def get_stock_minute_detail(code, response):
    data = json.loads(response)
    jsonArray = data["result"]["data"]
    result = []
    for item in jsonArray:
        map = {
            "price": item.get("p"),
            "vol": item.get("v"),
            "minute": item.get("m"),  # Changed 'minuter' to 'minute' for consistency
            "avgPrice": item.get("avg_p")
        }
        result.append(map)
    return result

def get_stock_minuter_list(code):
    stock_minute_info = get_stock_minute_info(code)
    print(stock_minute_info)
    if stock_minute_info:
        return get_stock_minute_detail(code, stock_minute_info)
    else:
        return []


