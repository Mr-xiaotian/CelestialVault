import sys
import common_functions as cf

class Framer:
    def __init__(self, get_dictory, print_list, _pool):
        print_list = ['Unknowquestion',
                      'question id',
                      
                      ]
        self.texts_list = []
        self.id = 1
        self.error_text = ''
        
        self._pool = _pool
        
        pass

    def get_dictory(self) -> (list, str):
        return [],''

    def get_dictory_text(self, obj) -> str:
        return f'[{obj[0]}({obj[1]})](#{obj[0]}({obj[1]}))'

    def add_texts_list(self, dictory):
        self.threader.start(dictory, 'flock')
        self.texts_list += self.threader.getTextList()
            
        assert self.threader.error_flag, '\n\n' + \
                "\\".join(self.threader.error_text_list) + '下载出错'

    def return_iprint_di(self, dictory):
        return dictory

    def get_somethings(self, something_list = None):
        something_list = [i[0] for i in self.something_list] if something_list == None else something_list 
        self.error_list = []
        self.error_text = ''

        print(f'列表已更新，总共{len(something_list)}本书，现在开始下载.')
        for _id,num in cf.zip_range(something_list):
            self.something_id = str(_id)
            
            self.get_something()
            print(f'(num:{num+1}/{len(something_list)})')
            sleep(5)
            pass

        if self.error_list != []:
            print('\n下载完成，其中开启断点保护的文件有:')
            print(self.error_list)
            print(self.error_text)

    
    def get_something(self):
        try:
            name_add = ''
            #self.something_id = something_id
            self._pool.something_title = print_list[0]
            
            print(f'\n\n{print_list[1]}:{self.something_id}',)
            dictory = self.get_dictory()
            dictory_len = len(dictory)
            assert dictory_len > 0, '目录获取错误'
            cf.iprint(self.return_iprint_di(dictory))
            print()

            dictory_text = '\n'.join([self.get_dictory_text(d) \
                                      for d in dictory])
            self.texts_list.append('\n\n目录:')
            self.texts_list.append(dictory_text + '\n')
            #print(self.texts_list)

            begin_time = time()
            self.add_texts_list(dictory)

        except RequestError as e:
            self.error_text += '请求Html错误:\n' + str(e)
            #self.error_text += f'url:{kwargs["url"]}\n'
            #print('请求Html错误:\n',e)
            #print('url:',url,'\n')

        except Exception as e:
            print(e)
            print('\n出错！开始下载断点保护版', file = sys.stderr)
            
            self.error_list.append(self.question_id)
            name_add = '(断点保护版)'

        if locals().get('begin_time', None) != None:
            begin_time = begin_time
        else:
            begin_time = time()
        print(f'\n%.2fs'%(time() - begin_time))

        title = self._pool.suber.sub_name(title)
        self._pool.saver.add_path = f'问题\\{title}({self.something_id})'
        file_name = f'{title}{name_add}({self.question_id})'
        
        self.download_main(file_name)
        sleep(3)

    def download_main(self, file_name, texts_list = None, suffix_name = '.md'):
        texts_list = self.texts_list if texts_list == None else texts_list

        texts = '\n'.join(texts_list)
        texts = self.suber.clear_texts(texts, {})
        
        self._pool.saver.download_text(file_name, texts, suffix_name = suffix_name)
        name = os.path.split(file_name)[-1].split('.')[0]
        print(name, '文本下载完成', sep = '')

        self.texts_list = []
