import os
from datetime import datetime


class RunAll(object):
    def __init__(self, base_name):
        self.base_name = base_name

    def run(self):
        try:
            self.make_eqn_file()
            self.make_aig_from_eqn()
            acc = self.extract_data()
            self.make_verilog()
            self.compile_verilog()
        except Exception as e:
            raise e

        return acc

    def make_eqn_file(self):
        print(f'make_eqn_file ({self.base_name})')
        try:
            self.generate_logic()

            output_path = f'sop/{self.base_name}.eqn'

            remove = False
            with open(output_path) as fin:
                lines = fin.readlines()

                # c5.0 não aprendeu a árvore
                if 'f1 = ;' in lines[2]:
                    remove = True
            if remove:
                os.system(f'rm {output_path}')
                raise Exception('C5.0 não aprendeu a árvore')

        except Exception as e:
            raise Exception(f'Error 2: {e}')

    def generate_logic(self):
        print(f'generate_logic ({self.base_name})')
        try:
            all_attributes = set()
            with open(f'trees/{self.base_name}.tree') as fin:
                lines = [line.strip('\n') for line in fin.readlines()]
                line_start = [idx for (idx, line) in enumerate(lines) if ('Decision tree:' in line)][0] + 2 
                line_end = [idx for (idx, line) in enumerate(lines[line_start:]) if line == ''][0] + line_start
                n_attributes = int([line.split('(')[1].split()[0] for line in lines if 'attributes)' in line][0])
                
                # casos em que C5.0 nao aprendeu!
                if line_start == line_end:
                    sop = lines[line_start-1].split('(')[0]
                else:
                    prods = []
                    prod_vars = []
                    for line in lines[line_start:line_end]:
                        
                        is_leaf = '(' in line
                        
                        var, val = line.split('=')
                        var_pos = len(var.split('X')[0])//4
                        var = var.split('.')[-1].replace(' ', '').replace(':', '')
                        val = val.split(':')[-2].replace(' ', '')
                        all_attributes.add(var)
                        var = '!'*(val == '0')+var
                        
                        try:
                            prod_vars[var_pos] = var
                        except:
                            prod_vars.append(var)
                        
                        if is_leaf:
                            decision = line.split(':')[-1].split()[0]
                            if decision == '1':
                                prods.append('*'.join(prod_vars[:var_pos+1]))

                    sop = ' + '.join(prods)
                expression = sop
                
            with open(f'sop/{self.base_name}.eqn', 'w') as fout:
                header = 'INORDER = '
                header += ' '.join([f'X{i}' for i in range(n_attributes-1)])
                header += ';\nOUTORDER = f1;\n'
                final_expression = header + 'f1 = ' + expression + ';'
                print(final_expression, file=fout)

        except Exception as e:
            raise Exception(f'Error 3: {e}')

    def make_aig_from_eqn(self):
        print(f'make_aig_from_eqn ({self.base_name})')
        try:
            with open('temp/make_aig_from_eqn_script', 'w') as fout:
                print(f'read_eqn sop/{self.base_name}.eqn', file=fout)
                print('strash', file=fout)
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
        directory = f'verilog/{self.base_name}'
        os.mkdir(directory)

        verilog_file = self.base_name + '.v'

        with open('temp/make_verilog_script', 'w') as fout:
            print(f'read_aiger aig/{self.base_name}.aig\nwrite_verilog {directory}/{verilog_file}', file=fout)
        os.system('./abc -F temp/make_verilog_script')

        with open(f'{directory}/{verilog_file}', 'r') as fin:
            verilog = fin.read()

        verilog = verilog.replace('\\aig/', '')

        with open(f'{directory}/{verilog_file}', 'w') as fout:
            print(verilog, file=fout)

        print(f'{verilog_file} CREATED')

    def compile_verilog(self):
        os.system(f'quartus_map verilog/{self.base_name}/{self.base_name}')
        os.system(f'quartus_fit verilog/{self.base_name}/{self.base_name}')
        os.system(f'quartus_sta verilog/{self.base_name}/{self.base_name}')
        os.system(f'quartus_eda verilog/{self.base_name}/{self.base_name}')
