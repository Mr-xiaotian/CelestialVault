# -*- coding: utf-8 -*-
#版本 1.01
#作者：晓天

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
    ]

zh_headers_test = '''
accept: */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
cookie: _xsrf=7xICsu5O8PE87zwY3V9Bk0guc1w3pthZ; _zap=90264175-7e1c-4046-993c-3652ab7db4db; d_c0="AOBaQb5p1xCPTsYxy9cFRz22MK09C8BhMEU=|1582114032"; _ga=GA1.2.645135066.1582888444; __utmv=51854390.100--|2=registration_date=20170823=1^3=entry_date=20170823=1; __utma=51854390.645135066.1582888444.1584976406.1585148452.3; tst=r; q_c1=2152116e8d094a10ad9afd4e69c9df32|1602335122000|1583306511000; r_cap_id="NjNjNWFhNmExZWRmNDM2NGFkOGUwNjc0YTEwNWEzYTA=|1603426933|27b25945f9a11e94f601fe8cc53d0828b6eb9e8a"; cap_id="MGZjMDA1ZmY3ZGYwNGE1NmE5ZDcxMWIyYTQ4ODRkNjk=|1603426933|f40dc3f7a0df795a3eaec6532f2a97a81ec878c6"; l_cap_id="NmNlODFlYjZlOWU0NDQxMGEyYTY2YzU5MzQxNDY4OWQ=|1603433670|e3e9d9fbfa3109692e607785792a46d124564810"; capsion_ticket="2|1:0|10:1603852797|14:capsion_ticket|44:ZWRiMTI2NmM2ZWRmNDNhMWFjMjZmYmM4N2U0MGRlYmI=|d6e6d8ac56a84d4ad5ca8309434037d80b5fb3dda8e68334ff988aaf4bb1f5d6"; z_c0="2|1:0|10:1603852810|4:z_c0|92:Mi4xUVhiR0JRQUFBQUFBNEZwQnZtblhFQ1lBQUFCZ0FsVk5DaWlHWUFETER2cmR5WVppTzI1M3ZJeGN0cHVZSXRod3Jn|30bc86a97327e49f813decf8a965efaa8ccff3e843003ba2edad588d22937cfc"; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1603790080,1603852688,1603855130,1603880752; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1604026038; SESSIONID=MKw2TMvPzjcywk7ekKscAk7T9e7fYnkDUMyhlIggUhL; JOID=VV8SA0Peaayl00ghP9nm8ciWArwukyLcn4gFV2irA8_brCwWWmgQOP3cSCYwT3fEBrTQXqrievs2EqY8fk6zVmY=; osd=UFETC07bZ62t3k0vPtHr9MaXCrErnSPUko0LVmCmBsHapCETVGkYNfjSSS49SnnFDrnVUKvqd_44E64xe0CyXms=; KLBRSID=76ae5fb4fba0f519d97e594f1cef9fab|1604026096|1604024093
pragma: no-cache
referer: https://www.zhihu.com/search?type=content&q=%E9%9C%B8%E7%8E%8B%E9%BE%99
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.116 Safari/537.36
x-ab-param: tp_zrec=1;se_col_boost=1;tsp_hotlist_ui=1;se_ffzx_jushen1=0;zr_slotpaidexp=9;tp_dingyue_video=0;li_panswer_topic=0;ls_video_commercial=0;qap_question_author=0;qap_question_visitor= 0;pf_noti_entry_num=2;li_catalog_card=1;li_edu_page=old;tp_clubhyb=1;top_test_4_liguangyi=1;li_video_section=1;tp_contents=1;li_svip_tab_search=1;li_vip_verti_search=0;li_sp_mqbk=0;pf_adjust=1;zr_expslotpaid=1;zr_intervene=0;tp_topic_style=0;li_paid_answer_exp=0;pf_profile2_tab=0;zr_sim3=0;zw_sameq_sorce=999
x-ab-pb: Ckb0CyYMJwpYC+ALPgtSC0sLYAvPCw8MmgvXC5YLhgvhC7ULBwwADPMLIgzcC0wLJQrkCpsLDwu5CwEL7AogDKwLIQy0ChILEiMAAAYAAAEBAQALAAAAAAEBAwAAAQAAAAUAAgAAAQEAAQAAAA==
x-api-version: 3.0.91
x-app-za: OS=Web
x-requested-with: fetch
x-zse-83: 3_2.0
x-zse-86: 1.0_aXNqFh9q2_NYUhtqM8xqQQ90rM2x27F0ZwFBHDUqS_SX
'''
