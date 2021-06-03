import os
import numpy as np
import train_trees
from copy import deepcopy
import create_top_level_entities
from datetime import datetime


DIRECTORY = 'temp'


class RunAll(object):
    def __init__(self, base_name, xtr=list(), ytr=list(), feature_names=list()):
        self.base_name = base_name
        self.xtr = xtr
        self.ytr = ytr
        self.feature_names = feature_names

    def run(self):
        try:
            self.make_eqn_file()
            self.make_aig_from_eqn()
            acc = self.extract_aig_data()
            self.make_verilog()
            # self.compile_verilog()
        except Exception as e:
            raise e

        return acc

    def make_eqn_file(self):
        tree, acc_tree = train_trees.trainTree(self.xtr, self.ytr)

        sop = train_trees.pythonizeSOP(train_trees.treeToSOP(tree, self.feature_names))

        x_amt = len(self.feature_names)
        sop_header = 'INORDER = '
        sop_header += ' '.join([f'x{i:02d}' for i in range(x_amt)]) + ';\nOUTORDER = z0;\nz0 = '
        sop = sop_header + sop + ';'

        with open(f'sop/{self.base_name}.eqn', 'w') as fout:
            print(sop, file=fout)

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

    def extract_aig_data(self):
        print(f'extract_aig_data ({self.base_name})')
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
        path = f'verilog/{self.base_name}/{self.base_name}'
        print(f'quartus_map --read_settings_files=on --write_settings_files=off {path} -c {path}')
        os.system(f'quartus_map --read_settings_files=on --write_settings_files=off {path} -c {path}')
        os.system(f'quartus_fit --read_settings_files=off --write_settings_files=off {path} -c {path}')
        os.system(f'quartus_asm --read_settings_files=off --write_settings_files=off {path} -c {path}')
        os.system(f'quartus_sta {path} -c {path}')
        os.system(f'quartus_eda --read_settings_files=off --write_settings_files=off {path} -c {path}')

        # os.system(f'quartus_map verilog/{self.base_name.split("_out_")[0]}/{self.base_name}')
        # os.system(f'quartus_fit verilog/{self.base_name.split("_out_")[0]}/{self.base_name}')
        # os.system(f'quartus_sta verilog/{self.base_name.split("_out_")[0]}/{self.base_name}')
        # os.system(f'quartus_eda verilog/{self.base_name.split("_out_")[0]}/{self.base_name}')
    
    def extract_synthesis_data(self):
        with open(f'verilog/{self.base_name}/output_files/{self.base_name}.flow.rpt', 'r') as fin, open(f'verilog/{self.base_name}/synthesis_results.txt', 'w') as fout:
            for line in fin.readlines():
                if 'Logic utilization' in line:
                    print(f'Logic utilization: {line.split(";")[2].strip()}', file=fout)
                elif 'Total pins' in line:
                    print(f'Total pins: {line.split(";")[2].strip()}', file=fout)
                    break

