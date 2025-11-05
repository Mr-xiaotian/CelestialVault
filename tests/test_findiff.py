import pytest, logging
from celestialvault.instances.inst_findiff import Findiffer
from celestialvault.tools.TextTools import str_to_dict


def test_fd_str():
    str_0 = "1657"
    str_1 = "1626"

    str_2 = "1234dtyjdtyjdtyj6789"
    str_3 = "123456789"

    str_4 = "1239945"
    str_5 = "2923476"

    str_6 = "WBtopGlobal_register_version=2021070916"
    str_7 = "wb_view_log=1536*8641.25"

    str_8 = "GGT"
    str_9 = "GTT"

    str_10 = "132"
    str_11 = "456"

    # Create an instance of the Findiffer class
    findiffer = Findiffer("[", "]", "[]")
    print("\n")

    findiffer.fd_str(str_0, str_1)
    findiffer.fd_str(str_2, str_3)
    findiffer.fd_str(str_4, str_5)
    findiffer.fd_str(str_6, str_7)
    findiffer.fd_str(str_8, str_9)
    findiffer.fd_str(str_10, str_11)


def test_fd_dict():
    str_0 = "SINAGLOBAL=726498192962.7856.1581590581551; UOR=,,news.youth.cn; login_sid_t=015292a8ba72d856cae5b22680861963; cross_origin_proto=SSL; _s_tentry=-; Apache=3595127495457.271.1625819725620; ULV=1625819725627:19:1:1:3595127495457.271.1625819725620:1624162772348; WBtopGlobal_register_version=2021070916; SSOLoginState=1625820399; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5PeVRUQONGCM8Rrd.b8s8Q5JpX5KMhUgL.Fozpe0.feKn4S052dJLoIEXLxKqL1K.L1KeLxK-LBKBLBK.LxK-LBo5L12qLxKqL1h5LB-2LxK-L1h-LB.Bt; ALF=1657470788; SCF=Am5owQxxc637SAPKvQuZb_j2-EoihJ0mZBomjE-9lR41CwUPDNHpxA8VF1072DCgdIppH2FjWGMjJ7cacwvJ8qk.; SUB=_2A25N7buVDeRhGeRP6FsU8SbFzDyIHXVumqpdrDV8PUNbmtB-LUnZkW9NTj0tqlPrTQaSyU8mnRR2ZDR0LYkD84nn; wb_view_log_2139518970=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1625974572289%2C%22dm_pub_total%22%3A5%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A83%2C%22msgbox%22%3A0%7"
    str_1 = "SINAGLOBAL=726498192962.7856.1581590581551; UOR=,,news.youth.cn; login_sid_t=015292a8ba72d856cae5b22680861963; cross_origin_proto=SSL; _s_tentry=-; Apache=3595127495457.271.1625819725620; ULV=1625819725627:19:1:1:3595127495457.271.1625819725620:1624162772348; wb_view_log=1536*8641.25; WBtopGlobal_register_version=2021070916; SUB=_2A25N7Hy_DeRhGeRP6FsU8SbFzDyIHXVumOl3rDV8PUNbmtANLVPwkW9NTj0tqi9Nl4ydVcx1qWHVVDHgO5-bTJm6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5PeVRUQONGCM8Rrd.b8s8Q5JpX5o275NHD95QEeKe4SK2R1KM7Ws4Dqcj_i--ciK.4iK.0i--fi-2Xi-24i--fi-z7iKysi--ciKn7i-8Wi--fiKnfi-i2; ALF=1626425199; SSOLoginState=1625820399; wvr=6; wb_view_log_2139518970=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1625821623881%2C%22dm_pub_total%22%3A5%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A83%2C%22msgbox%22%3A0%7D"

    # Create an instance of the Findiffer class
    findiffer = Findiffer("[", "]", "[]")
    print("\n")

    # Test the findiff method
    str_0_dict = str_to_dict(str_0, line_delimiter=";", key_value_delimiter="=")
    str_1_dict = str_to_dict(str_1, line_delimiter=";", key_value_delimiter="=")
    findiffer.fd_dict(str_0_dict, str_1_dict)
