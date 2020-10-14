import os


class TreeMaker(object):
    def __init__(self, c50_files_path):
        self.c50_files_path = c50_files_path

    def make_tree(self, m: list = ['15']):
        for file_name in os.listdir(self.c50_files_path):
            for _m in m:
                if '.data' in file_name:
                    base_name = file_name.replace('.data', '')
                    print('./c5.0 -m ' + _m + ' -r -f ' + self.c50_files_path + '/' + base_name + ' > trees/' +
                          base_name + '_m_' + _m + '.tree.txt')
                    os.system('./c5.0 -m ' + _m + ' -r -f ' + self.c50_files_path + '/' + base_name + ' > trees/' +
                              base_name + '_m_' + _m + '.tree.txt')
                    remove = False
                    with open('trees/' + base_name + '_m_' + _m + '.tree.txt') as fin:
                        lines = fin.readlines()
                        # if int(lines[10].split()[1]) < 64:    sem o parametro -m no c50
                        if int(lines[11].split()[1].replace('(', '')) < 64:  # com o parametro -m
                            remove = True
                    if remove:
                        os.system('rm trees/' + base_name + '.tree.txt')
