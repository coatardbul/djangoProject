from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams


def get_sz_sz_type(code):
    if code[0:2] == "00":
        return TDXParams.MARKET_SZ;
    else:
        return TDXParams.MARKET_SH;


def refreshTickInfo(dateStr, code):
    dateFormatStr = dateStr.replace("-", "");
    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        data = api.get_history_transaction_data(get_sz_sz_type(code), code, 0, 2000, int(dateFormatStr))
        print(data)
    print(len(data))

    for i in range(len(data)):
        print(data[i])
    return "";
