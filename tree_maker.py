import os


class TreeMaker(object):
    @staticmethod
    def make_tree(benchmark_name, number_of_outputs):
        file_path = 'c50_files/files'
        for i in range(number_of_outputs):
            base_name = f'{benchmark_name}_out_{i}'
            print('./c5.0 -f ' + file_path + '/' + base_name + ' > trees/' + base_name + '.tree')
            os.system('./c5.0 -f ' + file_path + '/' + base_name + ' > trees/' + base_name +
                      '.tree')
            remove = False
            with open('trees/' + base_name + '.tree') as fin:
                lines = fin.readlines()
                if int(lines[9].split()[1]) < 64:
                    remove = True
            # if remove:
            #     os.system('rm trees/' + base_name + '.tree')
