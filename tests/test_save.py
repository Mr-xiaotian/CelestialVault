import pytest, logging, pprint
from time import time
from celestialvault.instances.inst_save import Saver

def test_saver():
    li = [
        'https://ttzytp.com/dongman/xvhu6d.jpg',
        'dfgdfgdfgdfg',
        'https://ttzytp.com/dongman/xvjq0t.jpg',
        'https://ttzytp.com/dongman/xvlwc7.jpg',
        'https://ttzytp.com/dongman/xvoi5z.jpg',
        # 'https://ttzytp.com/dongman/xvznus.jpg',
        # 'https://ttzytp.com/dongman/xw2j01.jpg',
        # 'https://ttzytp.com/dongman/xw4svq.jpg',
        # 'https://ttzytp.com/dongman/xw6sif.jpg',
        # 'https://ttzytp.com/dongman/xw9d0e.jpg',
        # 'https://ttzytp.com/dongman/xwkvsc.jpg',
        # 'https://ttzytp.com/dongman/xwne5w.jpg',
        # 'https://ttzytp.com/dongman/xwq5ud.jpg',
        # 'https://ttzytp.com/dongman/xwst1v.jpg',
        # 'https://ttzytp.com/dongman/xwv52q.jpg',
        # 'https://ttzytp.com/dongman/xx6sjn.jpg',
        # 'https://ttzytp.com/dongman/xx8ty1.jpg',
        # 'https://ttzytp.com/dongman/xxc8h6.jpg',
        # 'https://ttzytp.com/dongman/xxeni2.jpg',
        # 'https://ttzytp.com/dongman/xxgmgl.jpg',
        # 'https://ttzytp.com/dongman/xxrabi.jpg',
        # 'https://ttzytp.com/dongman/xxtftc.jpg',
        # 'https://ttzytp.com/dongman/xxvkih.jpg',
        # 'https://ttzytp.com/dongman/xxy5gf.jpg',
        # 'https://ttzytp.com/dongman/xy0965.jpg',
        # 'https://ttzytp.com/dongman/xy26a8.jpg',
        # 'https://ttzytp.com/dongman/xyd87f.jpg'
    ]

    saver = Saver(r'../test')
    saver.set_add_path('test_jpg')

    start_time = time()
    chain_mode = 'serial'

    task_list = [(num, i, '.jpg') for num,i in enumerate(li)]
    final_result_dict = saver.download_urls(task_list, chain_mode)
    logging.info(f'TaskChain completed in {time() - start_time} seconds by {chain_mode}.')
    logging.info(f"Task result: \n{pprint.pformat(final_result_dict)}.")

    # saver.fetch_threader.set_execution_mode('async')
    # saver.fetch_threader.start(task_list)
    # logging.info(f"Task result: {saver.fetch_threader.result_dict}.")


