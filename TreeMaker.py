import os


class TreeMaker(object):
    def __init__(self, c50_files_path):
        self.c50_files_path = c50_files_path

    def make_tree(self):
        for file_name in os.listdir(self.c50_files_path):
            if '.data' in file_name:
                base_name = file_name.replace('.data', '')
                print('./c5.0 -r -f ' + self.c50_files_path + '/' + base_name + ' > trees/' + base_name + '.tree.txt')
                os.system('./c5.0 -r -f ' + self.c50_files_path + '/' + base_name + ' > trees/' + base_name +
                          '.tree.txt')
                remove = False
                with open('trees/' + base_name + '.tree.txt') as fin:
                    lines = fin.readlines()
                    if int(lines[10].split()[1]) < 64:
                        remove = True
                if remove:
                    os.system('rm trees/' + base_name + '.tree.txt')
