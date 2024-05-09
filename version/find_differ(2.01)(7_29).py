# -*- coding: utf-8 -*-
#版本 2.01
#作者：晓天
import sys
from itertools import zip_longest
import common_functions as cf

def fd_str(a, b, split_str = '\n'):
    print(f'len(a):{len(a)}, len(b):{len(b)}\n')
    print(f'a与b不同的地方为(以{split_str}为划分):')

    a,b = cf.strings_spit(a, b, split_str=split_str)
    
    for i in range(min(len(a),len(b))):
        #print('这里是第%d行'%(i+1))
        if a[i] == b[i]:
            pass
        else:
            main_body(a[i],b[i])
            print('(第%d行)\n'%(i+1))

def fd_dict(dict_a,dict_b):
    # a_keys_values = [list(i) for i in zip(*dict_a.items())]    
    key_max,key_min,dif_key_a,dif_key_b = cf.dictkey_mix(
        dict_a,dict_b
        )
  
    for key in key_min:
        if dict_a[key] == dict_b[key]:
            pass
        else:
            print(key, ':')
            main_body(dict_a[key],dict_b[key])
            print()
            
    if dif_key_a != []:
        print('a中的特有标签值为：')
        for key in dif_key_a:
            print(f'{key} :\n{dict_a[key]}')
    print()
            
    if dif_key_b != []:
        print('b中的特有标签值为')
        for key in dif_key_b:
            print(f'{key} :\n{dict_b[key]}')
            
def main_body(u, v):
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

def prints(con, differ_list):
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
com_f = 'SINAGLOBAL=726498192962.7856.1581590581551; wvr=6; SSOLoginState=1626190483; _s_tentry=login.sina.com.cn; Apache=4977157209711.561.1626190485141; UOR=,,login.sina.com.cn; ULV=1626190486027:20:2:1:4977157209711.561.1626190485141:1625819725627; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5PeVRUQONGCM8Rrd.b8s8Q5JpX5KMhUgL.Fozpe0.feKn4S052dJLoIEXLxKqL1K.L1KeLxK-LBKBLBK.LxK-LBo5L12qLxKqL1h5LB-2LxK-L1h-LB.Bt; ALF=1657849268; SCF=Am5owQxxc637SAPKvQuZb_j2-EoihJ0mZBomjE-9lR41ao1TTanxfUq3-wg6IEJe94kCiSZj3y8gL9dyoS7YlTY.; SUB=_2A25N6-JlDeRhGeRP6FsU8SbFzDyIHXVugVStrDV8PUNbmtAKLUPjkW9NTj0tqjtKDsGX12zeBpv6dPu7Yl0x8EBx; wb_view_log_2139518970=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1626313340702%2C%22dm_pub_total%22%3A5%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A80%2C%22msgbox%22%3A0%7D'

com_g = '1234dtyjdtyjdtyj6789'
com_h = '123456789'

you_0 = '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'
you_1 = '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'

if __name__ == '__main__':
    #normal(com_a,com_b)
    #print(pr_dict(pro(com_a,com_b)))
    
    #dict_0 = cf.str_to_dict(com_c)
    #dict_1 = cf.str_to_dict(com_b)
    #dicts = cf.deal_cookie(com_d,com_f)
    #dict_0, dict_1 = dicts[0], dicts[1]
    #print(dict_0, '\n', dict_1)
    #fd_dict(dict_0,dict_1)

    normal(you_0, you_1, '/')
    pass
