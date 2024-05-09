# -*- coding: utf-8 -*-
#版本 1.01
#作者：晓天

def pro_slash(strs):
    #get_name/get_lyric中获得的网页文件中中文字符用unicode编码，如\u5c11,但所有转义符均被转义，如\\u5c11
    #此函数用来消除多余的转义符，例如'abc\\\\def\\\\ghi\\\\jk'
    re_strs = repr(strs)   #返回对象string格式，如"'abc\\\\\\\\def\\\\\\\\ghi\\\\\\\\jk'"
    pl_strs = re_strs.replace('\\\\', '\\')   #如"'abc\\\\def\\\\ghi\\\\jk'"
    if pl_strs[-2] == '\\':   #在下载monkey dance时，get_lyric进行错误处理，使传入值以\\结尾，eval后将'转义，在此进行临时处理
        print(pl_strs[1:-2])
        pro_strs = eval(pl_strs[1:-2])
        return pro_strs
    else:
        pro_strs = eval(pl_strs)   #如'abc\\def\\ghi\\jk'
        return pro_strs

def creat_folder(path):
    #判断系统是否存在该路径，没有则创建
    import os
    while True:
        try:
            if not os.path.exists(path):   
                os.makedirs(path)
            break
        except:
            path = path[:-1]
            continue
    return path

def str_to_dirt(strs):
    header = strs.split('\n')
    headers = {}
    
    while '' in header:
        header.remove('')
        
    for h in header:
        sp = h.partition(':')
        headers[sp[0]] = sp[2].strip()

    return headers


if __name__ == '__main__':
    headers = main(strs = test)
    import requests
    for i in headers:
        #print(i + ':' + headers[i])
        pass
    
    


