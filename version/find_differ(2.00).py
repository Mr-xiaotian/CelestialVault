# -*- coding: utf-8 -*-
#版本 2.00
#作者：晓天
import sys
from common_functions import str_to_dict

def pro(*strs):
    li = []
    i = 0
    for st in strs:
        li.append(st.split('\n'))
        
        while '' in li[i]:
            li[i].remove('')
        i += 1
    
    return li

def differ_mix(key_a,key_b):
    key_max = key_a[:]
    key_min = []
    dif_key_a = []
    dif_key_b = []
    
    for each in key_b:
        if each not in key_a:
            key_max.append(each)
            dif_key_b.append(each)
        else:
            key_min.append(each)
    for each in key_a:
        if each not in key_b:
            key_max.append(each)
            dif_key_a.append(each)
    
    return key_max,key_min,dif_key_a,dif_key_b

def deal_cookie(*cookies):
    cookie_dirts = []
    for cookie in cookies:
        cookie += '; '

        cookie_list = cookie.split('; ')
        cookie_dirt = {}
        for c_l in cookie_list:
            #print(c_l)
            key,_,value = c_l.partition('=')
            cookie_dirt[key] = value
        cookie_dirts.append(cookie_dirt)

    return cookie_dirts[0], cookie_dirts[1]

def normal(a,b):
    if a == b:
        print('a、b完全相同')
    else:
        print('a与b不同的地方为:')

        a,b = pro(a,b)
        
        for i in range(min(len(a),len(b))):
            #print('这里是第%d行'%(i+1))
            if a[i] == b[i]:
                pass
            else:
                main_body(a[i],b[i])
                print('(第%d行)\n'%(i+1))

def dirt(dirt_a,dirt_b):
    a_keys_values = [list(i) for i in zip(*dirt_a.items())]
    b_keys_values = [list(i) for i in zip(*dirt_b.items())]
            
    key_max,key_min,differ_key_a,differ_key_b = differ_mix\
                                                (a_keys_values[0],b_keys_values[0])
  
    for key in key_min:
        if dirt_a[key] == dirt_b[key]:
            pass
        else:
            print(key + ':',sep = '')
            main_body(dirt_a[key],dirt_b[key])
            print()
            
    if differ_key_a != []:
        print('a中的特有标签值为：')
        for key in differ_key_a:
            print(key + ':\n',dirt_a[key],sep = '')
    print()
            
    if differ_key_b != []:
        print('b中的特有标签值为')
        for key in differ_key_b:
            print(key + ':\n',dirt_b[key],sep = '')
            
def main_body(u,v):
    num = 0
    differ_start = -1
    differ_list = []
    max_one = u[:] if len(u) >= len(v) else v[:]
    min_one = v[:] if len(u) >= len(v) else u[:]

    if u == v:
        print('完全一致')
        return
    
    for j in range(len(min_one)):
        if u[j] == v[j] and differ_start != -1 and \
            u[differ_start:differ_end+1] != '':
            
            differ_list.append((differ_start, differ_end+1))
            differ_start = -1
            pass
        elif u[j] != v[j]:
            differ_end = j
            if differ_start == -1 or u[j-1] == v[j-1]:
                differ_start = j
        else:
            differ_start = -1

    if differ_start != -1:
        differ_list.append((differ_start, len(max_one)))
    elif differ_list == []:
        differ_list.append((len(min_one), len(max_one)))
                
    prints(u,differ_list)
    prints(v,differ_list)

def prints(con,differ_list):
    temp = con[:]
    first_num = 0
    for num in differ_list:
        start_num,end_num = num
        end_num = len(temp) if end_num > len(temp) else end_num
        
        print(temp[first_num:start_num], end = '')
        print(temp[start_num:end_num], file = sys.stderr, end = '')
        first_num = end_num
    print(temp[first_num:])

com_a = '''
请求 URL: https://www.mmgal.com/music/api.php?callback=jQuery111307866832751924853_1596631037741
请求方法: POST
状态代码: 200 
远程地址: 104.31.68.200:443
引用站点策略: no-referrer-when-downgrade
alt-svc: h3-27=":443"; ma=86400, h3-28=":443"; ma=86400, h3-29=":443"; ma=86400
cf-cache-status: DYNAMIC
cf-ray: 5be08f792b52c340-SIN
cf-request-id: 046037ffb80000c340faa28200000001
content-encoding: br
content-type: application/json
date: Wed, 05 Aug 2020 12:35:52 GMT
expect-ct: max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"
server: cloudflare
status: 200
strict-transport-security: max-age=31536000; includeSubDomains; preload
vary: Accept-Encoding
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
x-xss-protection: 1; mode=block
:authority: www.mmgal.com
:method: POST
:path: /music/api.php?callback=jQuery111307866832751924853_1596631037741
:scheme: https
accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
content-length: 36
content-type: application/x-www-form-urlencoded; charset=UTF-8
cookie: __cfduid=d3bd8918eabaac7cbaf9cbb757529dafd1596276636; security_session_verify=8fc1488b33f525706490ff98537e8621
origin: https://www.mmgal.com
referer: https://www.mmgal.com/music/
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.50
x-requested-with: XMLHttpRequest
callback: jQuery111307866832751924853_1596631037741
types: url
id: 28918334
source: netease
'''

com_b = '''
请求 URL: https://www.mmgal.com/music/api.php?callback=jQuery111307866832751924853_1596631037741
请求方法: POST
状态代码: 200 
远程地址: 104.31.68.200:443
引用站点策略: no-referrer-when-downgrade
alt-svc: h3-27=":443"; ma=86400, h3-28=":443"; ma=86400, h3-29=":443"; ma=86400
cf-cache-status: DYNAMIC
cf-ray: 5be08f7edee7c340-SIN
cf-request-id: 04603803480000c340faa73200000001
content-encoding: br
content-type: application/json
date: Wed, 05 Aug 2020 12:35:52 GMT
expect-ct: max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"
server: cloudflare
status: 200
strict-transport-security: max-age=31536000; includeSubDomains; preload
vary: Accept-Encoding
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
x-xss-protection: 1; mode=block
:authority: www.mmgal.com
:method: POSTss
:path: /music/api.php?callback=jQuery111307866832751924853_1596631037741
:scheme: https
accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
content-length: 44
content-type: application/x-www-form-urlencoded; charset=UTF-8
cookie: __cfduid=d3bd8918eabaac7cbaf9cbb757529dafd1596276636; security_session_verify=8fc1488b33f525706490ff98537e8621
origin: https://www.mmgal.com
referer: https://www.mmgal.com/music/
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.50
x-requested-with: XMLHttpRequest
callback: jQuery111307866832751924853_1596631037741
types: pic
id: 8947825626942890
source: netease
'''

com_c = '''
请求 URL: https://www.mmgal.com/music/api.php?callback=jQuery111307866832751924853_1596631037743
请求方法: POST
状态代码: 200 
远程地址: 104.31.68.200:443
引用站点策略: no-referrer-when-downgrade
alt-svc: h3-27=":443"; ma=86400, h3-28=":443"; ma=86400, h3-29=":443"; ma=86400
cf-cache-status: DYNAMIC
cf-ray: 5be08f7edef1c340-SIN
cf-request-id: 046038034a0000c340faa75200000001
content-encoding: br
content-type: application/json
date: Wed, 05 Aug 2020 12:35:53 GMT
expect-ct: max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"
server: cloudflare
status: 200
strict-transport-security: max-age=31536000; includeSubDomains; preload
vary: Accept-Encoding
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
x-xss-protection: 1; mode=block
:authority: www.mmgal.com
:method: POST
:path: /music/api.php?callback=jQuery111307866832751924853_1596631037743
:scheme: https
accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
content-length: 38
content-type: application/x-www-form-urlencoded; charset=UTF-8
cookie: __cfduid=d3bd8918eabaac7cbaf9cbb757529dafd1596276636; security_session_verify=8fc1488b33f525706490ff98537e8621
origin: https://www.mmgal.com
referer: https://www.mmgal.com/music/
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.50
x-requested-with: XMLHttpRequest
callback: jQuery111307866832751924853_1596631037743
types: lyric
id: 28918334
source: netease
'''

com_d = 'SINAGLOBAL=726498192962.7856.1581590581551; UOR=,,news.youth.cn; login_sid_t=015292a8ba72d856cae5b22680861963; cross_origin_proto=SSL; _s_tentry=-; Apache=3595127495457.271.1625819725620; ULV=1625819725627:19:1:1:3595127495457.271.1625819725620:1624162772348; WBtopGlobal_register_version=2021070916; SSOLoginState=1625820399; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5PeVRUQONGCM8Rrd.b8s8Q5JpX5KMhUgL.Fozpe0.feKn4S052dJLoIEXLxKqL1K.L1KeLxK-LBKBLBK.LxK-LBo5L12qLxKqL1h5LB-2LxK-L1h-LB.Bt; ALF=1657470788; SCF=Am5owQxxc637SAPKvQuZb_j2-EoihJ0mZBomjE-9lR41CwUPDNHpxA8VF1072DCgdIppH2FjWGMjJ7cacwvJ8qk.; SUB=_2A25N7buVDeRhGeRP6FsU8SbFzDyIHXVumqpdrDV8PUNbmtB-LUnZkW9NTj0tqlPrTQaSyU8mnRR2ZDR0LYkD84nn; wb_view_log_2139518970=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1625974572289%2C%22dm_pub_total%22%3A5%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A83%2C%22msgbox%22%3A0%7'
com_e = 'SINAGLOBAL=726498192962.7856.1581590581551; UOR=,,news.youth.cn; login_sid_t=015292a8ba72d856cae5b22680861963; cross_origin_proto=SSL; _s_tentry=-; Apache=3595127495457.271.1625819725620; ULV=1625819725627:19:1:1:3595127495457.271.1625819725620:1624162772348; wb_view_log=1536*8641.25; WBtopGlobal_register_version=2021070916; SUB=_2A25N7Hy_DeRhGeRP6FsU8SbFzDyIHXVumOl3rDV8PUNbmtANLVPwkW9NTj0tqi9Nl4ydVcx1qWHVVDHgO5-bTJm6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5PeVRUQONGCM8Rrd.b8s8Q5JpX5o275NHD95QEeKe4SK2R1KM7Ws4Dqcj_i--ciK.4iK.0i--fi-2Xi-24i--fi-z7iKysi--ciKn7i-8Wi--fiKnfi-i2; ALF=1626425199; SSOLoginState=1625820399; wvr=6; wb_view_log_2139518970=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1625821623881%2C%22dm_pub_total%22%3A5%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A83%2C%22msgbox%22%3A0%7D'
if __name__ == '__main__':
    #normal(com_a,com_b)
    #print(pr_dict(pro(com_a,com_b)))
    
    dirt_0 = str_to_dict(com_c)
    dirt_1 = str_to_dict(com_b)
    #dirt_0, dirt_1 = deal_cookie(com_d,com_e)
    dirt(dirt_0,dirt_1)
    pass
