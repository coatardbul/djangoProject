def convert_buy_sell_flag(flag):
    if flag==2:
        return "EQUAL"
    if flag==1:
        return "DOWN"
    if flag==0:
        return "UP"
    return "";