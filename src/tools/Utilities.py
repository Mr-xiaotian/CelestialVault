from time import strftime, localtime


def get_now_time():
    return strftime("%Y-%m-%d", localtime())