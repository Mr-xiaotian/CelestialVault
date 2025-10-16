import pytest, logging, pprint
from time import time
from celestialvault.instances.inst_save import Saver

def test_saver():
    li = [
        'https://th.bing.com/th/id/OSK.3f6a54105e902fae371a5bb4883d3c2c?w=102&h=102&c=7&o=6&cb=12&pid=SANGAM',
        'dfgdfgdfgdfg',
        'https://th.bing.com/th/id/OIP.AmHF-jb62qAKtIX8ATelMQHaEs?w=80&h=80&c=1&bgcl=18953f&r=0&o=7&cb=12&pid=ImgRC&rm=3',
    ]

    saver = Saver(r'../test')
    saver.set_add_path('test_jpg')

    start_time = time()
    chain_mode = 'serial'

    task_list = [(i, num, '.jpg') for num,i in enumerate(li)]
    final_result_dict = saver.download_urls(task_list, chain_mode)
    logging.info(f'TaskChain completed in {time() - start_time} seconds by {chain_mode}.')
    logging.info(f"Task result: \n{pprint.pformat(final_result_dict)}.")

    # saver.fetch_threader.set_execution_mode('async')
    # saver.fetch_threader.start(task_list)
    # logging.info(f"Task result: {saver.fetch_threader.result_dict}.")


