import os


class TreeMaker(object):
    @staticmethod
    def make_tree(base_name):
        file_path = 'c50_files/files'

        os.system('./c5.0 -f ' + file_path + '/' + base_name + ' > trees/' + base_name + '.tree')

        remove = False
        with open('trees/' + base_name + '.tree') as fin:
            lines = fin.readlines()
            if int(lines[9].split()[1]) < 64:
                remove = True
        if remove:
            os.system('rm -f trees/' + base_name + '.tree')
        else:
            print(f'{base_name}.tree FILE CREATED')
