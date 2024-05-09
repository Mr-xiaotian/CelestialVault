# -*- coding: utf-8 -*-
#版本 1.04
#作者：晓天
import sys

def prints(con,differ):
    temp = con
    for num_i in differ:
        #print(num_i)
        #print(temp.partition(num_i))
        print(temp.partition(num_i)[0],end = '')
        print(temp.partition(num_i)[1],file = sys.stderr,end = '')
        temp = temp.partition(num_i)[2]
    print(temp)

def pro(*strs):
    li = []
    i = 0
    
    for st in strs:
        li.append(st.split('\n'))
    
        while '' in li[i]:
            li[i].remove('')

        i += 1
    
    return li

def pr_dict(*lists):
    li_dicts = []
    i = 0
    
    for lis in lists:
        
        for li in lis:
            dicts = {}
            
            for l in li:
                ty = l.partition(':')
                dicts[ty[0]] = ty[2]
                
            li_dicts.append(dicts)
            
        i += 1
        
    return li_dicts

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
            dif_key_a.append(each)
    
    return key_max,key_min,dif_key_a,dif_key_b
        
         
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

def url(a,b):
    a,b = pr_dict(pro(a,b))

    a_keys_values = [list(i) for i in zip(*a.items())]
    b_keys_values = [list(i) for i in zip(*b.items())]
            
    key_max,key_min,differ_key_a,differ_key_b = differ_mix\
                                                (a_keys_values[0],b_keys_values[0])
    
    for key in key_min:
        if a[key] == b[key]:
            pass
        else:
            print(key + ':',sep = '')
            main_body(a[key],b[key])
            print()
            
    if differ_key_a != []:
        print('a中的特有标签值为：')
        for key in differ_key_a:
            print(key + ':\n',a[key],sep = '')
    print()
            
    if differ_key_b != []:
        print('b中的特有标签值为')
        for key in differ_key_b:
            print(key + ':\n',b[key],sep = '')
            
def main_body(u,v):
    num = 0
    differ_start = -1
    differ_u = []
    differ_v = []
                
    for j in range(min(len(u),len(v))):
        if u[j] == v[j] and differ_start != -1 and \
            u[differ_start:differ_end+1] != '':
            differ_u.append(u[differ_start:differ_end+1])
            differ_v.append(v[differ_start:differ_end+1])
            differ_start = -1
            pass
        elif u[j] != v[j]:
            differ_end = j
            if differ_start == -1 or u[j-1] == v[j-1]:
                differ_start = j
        else:
            differ_start = -1

    if differ_start != -1:
        if len(u) > len(v):            
            differ_u.append(u[differ_start:])
            differ_v.append(v[differ_start:differ_end+1])
        elif len(v) > len(u):            
            differ_u.append(u[differ_start:differ_end+1])
            differ_v.append(v[differ_start:])
        else:
            differ_u.append(u[differ_start:])
            differ_v.append(v[differ_start:])
                
    #此处存在一个未解决的BUG，由于prints的逻辑是找最近的differ，
    #所以存在匹配出错的可能
    prints(u,differ_u)
    prints(v,differ_v)     

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
:method: POST
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

if __name__ == '__main__':
    #normal(com_a,com_b)
    #print(pr_dict(pro(com_a,com_b)))
    url(com_a,com_c)
    pass
