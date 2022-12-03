import time

def  get_now_tick(code):
    now = int(time.time())
    # 转换为其他日期格式，如："%Y-%m-%d %H:%M:%S"
    timeArr = time.localtime(now)
    other_StyleTime = time.strftime("%Y-%m-%d", timeArr)
    return other_StyleTime+"_tick_"+code;

def  get_his_tick(hisTime,code):
    return hisTime+"_tick_"+code;