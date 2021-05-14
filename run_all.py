import os
import numpy as np
import train_trees
import create_top_level_entities
from datetime import datetime


TREE_FILES_PATH = 'c50_files/files'


class RunAll(object):
    def __init__(self, base_name):
        self.base_name = base_name

    def run(self):
        try:
            self.make_eqn_file()
            self.make_aig_from_eqn()
            acc = self.extract_data()
            self.make_verilog()
            # self.compile_verilog()
        except Exception as e:
            raise e

        return acc

    def make_eqn_file(self):
        print('1')
        _train_data = np.loadtxt(f'{TREE_FILES_PATH}/{self.base_name}_temp.data', dtype='int', delimiter=',')
        test_data = _train_data
        feature_names = list(map(str, list(range(_train_data.shape[1]))))
        tree, acc_tree = train_trees.trainTree(_train_data, test_data)
        print('2')

        sop = train_trees.pythonizeSOP(train_trees.treeToSOP(tree, feature_names))
        print('3')

        x_amt = len(_train_data[0]) - 1
        sop_header = 'INORDER = '
        sop_header += ' '.join([f'x{i:02d}' for i in range(x_amt)]) + ';\nOUTORDER = z0;\nz0 = '
        sop = sop_header + sop + ';'

        with open(f'sop/{self.base_name}.eqn', 'w') as fout:
            print(sop, file=fout)
        print(sop)

    def make_aig_from_eqn(self):
        print(f'make_aig_from_eqn ({self.base_name})')
        try:
            with open('temp/make_aig_from_eqn_script', 'w') as fout:
                print(f'read_eqn sop/{self.base_name}.eqn', file=fout)
                print('strash', file=fout)
                # print('compress2rs', file=fout)
                print(f'write_aiger aig/{self.base_name}.aig', file=fout)
            os.system('./abc -F temp/make_aig_from_eqn_script')

        except Exception as e:
            raise Exception(f'Error 4: {e}')

    def extract_data(self):
        print(f'extract_data ({self.base_name})')
        with open('temp/mltest_script', 'w') as fout:
            print(f'&r aig/{self.base_name}.aig; &ps; &mltest temp/{self.base_name.replace("_temp", "")}.pla',
                  file=fout)

        mltest_out = './mltest/' + self.base_name + '_mltest.txt'
        os.system('./abc -F temp/mltest_script > ' + mltest_out)

        try:
            with open('sop_table_results.csv', 'r') as fin:
                table_results = fin.readlines()
        except Exception as e:
            raise Exception(f'Error 5: {e}')

        try:
            with open('sop_table_results.csv', 'w') as fout, open(mltest_out, 'r') as fin:
                mltest_lines = fin.readlines()
                try:
                    ands = mltest_lines[3].split()[8][:-4]
                    levs = mltest_lines[3].split()[11][:-4]
                    acc = mltest_lines[5].split()[9].replace('(', '')
                    if acc == '':
                        acc = mltest_lines[5].split()[10]
                    results = f'{self.base_name},{ands},{levs},{acc}'
                    table_results.append(results + '\n')
                except Exception as e:
                    raise Exception(f'Error 6: {e}')
                finally:
                    fout.writelines(table_results)
        except Exception as e:
            raise Exception(f'Error 7: {e}')

        return acc

    def make_verilog(self):
        directory = f'verilog/{self.base_name.split("_out_")[0]}'

        verilog_file = self.base_name.replace('_temp', '') + '.v'

        with open('temp/make_verilog_script', 'w') as fout:
            print(f'read_aiger aig/{self.base_name}.aig\nwrite_verilog {directory}/{verilog_file}',
                  file=fout)
        os.system('./abc -F temp/make_verilog_script')

        with open(f'{directory}/{verilog_file}', 'r') as fin:
            verilog = fin.read()

        verilog = verilog.replace('\\aig/', '').replace('-', '_').replace('_temp', '')

        with open(f'{directory}/{verilog_file}', 'w') as fout:
            print(verilog, file=fout)

        print(f'{verilog_file} CREATED')

    def compile_verilog(self):
        os.system(f'quartus_map verilog/{self.base_name.split("_out_")[0]}/{self.base_name}')
        os.system(f'quartus_fit verilog/{self.base_name.split("_out_")[0]}/{self.base_name}')
        os.system(f'quartus_sta verilog/{self.base_name.split("_out_")[0]}/{self.base_name}')
        os.system(f'quartus_eda verilog/{self.base_name.split("_out_")[0]}/{self.base_name}')
