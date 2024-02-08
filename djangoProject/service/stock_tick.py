from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams


def get_sz_sz_type(code):
    if (code[0:2] == "00" or code[0:2] == "30"):
        return TDXParams.MARKET_SZ;
    else:
        return TDXParams.MARKET_SH;


