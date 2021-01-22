import os
from datetime import datetime


class RunAll(object):
    def __init__(self, path):
        self.path = path
        self.base_name = self.path.split('.')[0]

    def run(self):
        try:
            self.make_eqn_file()
            self.make_aig_from_eqn()
            self.extract_data()
            # self.make_verilog()
            # self.create_quartus_files()
            #self.compile_verilog()

        except Exception as e:
            raise e

    def make_eqn_file(self):
        # print(f'make_eqn_file ({self.path})')
        try:
            if '.tree' in self.path:
                self.generate_logic()

            output_path = str(f'sop/{self.path.replace("tree", "eqn")}')

            remove = False
            with open(output_path) as fin:
                lines = fin.readlines()
                if 'f1 = ;' in lines[2]:    # c5.0 não aprendeu a árvore
                    remove = True
            if remove:
                os.system(f'rm {output_path}')
                raise Exception('C5.0 não aprendeu a árvore')

            self.path = self.path.replace('tree', 'eqn')

        except Exception as e:
            raise Exception(f'Error 2: {e}')

    def generate_logic(self):
        # print(f'generate_logic ({input_path})')
        try:
            expression = ''
            s = []  # sum
            n_attributes = 0
            all_attributes = set()
            prev_line = ''
            with open(f'trees/{self.path}') as fin:
                lines = [line.strip('\n') for line in fin.readlines()]
                line_start = [idx for (idx, line) in enumerate(lines) if ('Decision tree:' in line)][0] + 2 
                line_end = [idx for (idx, line) in enumerate(lines[line_start:])  if line == '' ][0] + line_start
                n_attributes = int([line.split('(')[1].split()[0] for line in lines if 'attributes)' in line][0])
                
                # casos em que C5.0 nao aprendeu!
                if line_start == line_end:
                    sop = lines[line_start-1].split('(')[0]
                else:   
                    sop = []
                    prods = []
                    prod_vars = []
                    for line in lines[line_start:line_end]:
                        
                        is_leaf = '(' in line
                        
                        var, val = line.split('=')
                        var_pos = len(var.split('X')[0])//4
                        var = var.split('.')[-1].replace(' ','').replace(':','')
                        val = val.split(':')[-2].replace(' ','')
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
                
            with open(f'sop/{self.path.replace("tree", "eqn")}', 'w') as fout:
                header = 'INORDER = '
                header += ' '.join([f'X{i}' for i in range(n_attributes-1)])
                header += ';\nOUTORDER = f1;\n'
                final_expression = header + 'f1 = ' + expression + ';'
                print(final_expression, file=fout)

        except Exception as e:
            raise Exception(f'Error 3: {e}')

    def make_aig_from_eqn(self):
        # print(f'make_aig_from_eqn ({self.path})')
        try:
            if '.eqn' in self.path:
                with open('temp/make_aig_from_eqn_script', 'w') as fout:
                    print(f'read_eqn sop/{self.path}', file=fout)
                    print('strash', file=fout)
                    print(f'write_aiger aig/{self.path.replace("eqn", "aig")}', file=fout)
                os.system('./abc -F temp/make_aig_from_eqn_script')
                self.path = self.path.replace('eqn', 'aig')
        except Exception as e:
            raise Exception(f'Error 4: {e}')

    def extract_data(self):
        # print(f'extract_data ({self.path})')
        with open('temp/mltest_script', 'w') as fout:
            output_number = ''
            if self.path[-5].isnumeric():
                if self.path[-6].isnumeric():
                    output_number = self.path[-6] + self.path[-5]
                else:
                    output_number = self.path[-5]
            print(f'&r aig/{self.path}; &ps; &mltest temp/temp_out_{output_number}.pla', file=fout)

        mltest_out =  './mltest/' + self.path + '_mltest.txt'
        os.system('./abc -F temp/mltest_script > ' + mltest_out)

        try:
            with open(f'sop_table_results.csv', 'r') as fin:
                table_results = fin.readlines()
        except Exception as e:
            raise Exception(f'Error 5: {e}')

        try:
            with open(f'sop_table_results.csv', 'w') as fout, open(mltest_out, 'r') as fin:
                mltest_lines = fin.readlines()
                try:
                    ands = mltest_lines[3].split()[8][:-4]
                    levs = mltest_lines[3].split()[11][:-4]
                    acc = mltest_lines[5].split()[9].replace('(', '')
                    if acc == '':
                        acc = mltest_lines[5].split()[10]
                    results = f'{self.path},{ands},{levs},{acc}'
                    table_results.append(results + '\n')
                except Exception as e:
                    raise Exception(f'Error 6: {e}')
                finally:
                    fout.writelines(table_results)
        except Exception as e:
            raise Exception(f'Error 7: {e}')

    def make_verilog(self):
        directory = f'verilog/{self.path.split(".")[0]}'
        os.mkdir(directory)
        verilog_file = self.path.replace("aig", "v")
        with open('temp/make_verilog_script', 'w') as fout:
            print(f'read_aiger aig/{self.path}\n'
                  f'write_verilog {directory}/{verilog_file}', file=fout)
        os.system('./abc -F temp/make_verilog_script')

        with open(f'{directory}/{verilog_file}', 'r') as fin:
            verilog = fin.read()

        verilog = verilog.replace('\\aig/', '')

        with open(f'{directory}/{verilog_file}', 'w') as fout:
            print(verilog, file=fout)

        print(f'{verilog_file} CREATED')

    def create_quartus_files(self):
        month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                      'October', 'November', 'December']

        project_name = self.base_name

        time = datetime.now().strftime("%H:%M:%S")

        month_number = datetime.today().date().month
        month = month_list[month_number - 1]

        day = str(datetime.today().day).zfill(2)

        year = datetime.today().year

        with open('verilog/QPF.qpf', 'r') as qpf, open('verilog/QSF.qsf', 'r') as qsf:
            qpf_lines = qpf.readlines()
            qsf_lines = qsf.readlines()

        qpf_output = ''
        for i in range(len(qpf_lines)):
            if i == 21:
                qpf_output += f'# Date created = {time}  {month} {day}, {year}\n'
            elif i == 26:
                qpf_output += f'DATE = \"{time}  {month} {day}, {year}\"\n'
            elif i == 30:
                qpf_output += f'PROJECT_REVISION = \"{project_name}\"'
            else:
                qpf_output += qpf_lines[i]

            qsf_output = ''
            for i in range(len(qsf_lines)):
                if i == 21:
                    qsf_output += f'# Date created = {time}  {month} {day}, {year}\n'
                elif i == 28:
                    qsf_output += f'#       {project_name}_assignment_defaults.qdf\n'
                elif i == 41:
                    qsf_output += f'set_global_assignment -name TOP_LEVEL_ENTITY {project_name}\n'
                elif i == 43:
                    qsf_output += f'set_global_assignment -name PROJECT_CREATION_TIME_DATE \"{time}  {month.upper()} ' \
                                  f'{day}, {year}\"\n'
                else:
                    qsf_output += qsf_lines[i]

            with open(f'verilog/{self.base_name}/{self.base_name}.qpf', 'w') as qpf, \
                    open(f'verilog/{self.base_name}/{self.base_name}.qsf', 'w') as qsf:
                print(qpf_output, file=qpf)
                print(qsf_output, file=qsf)

        print(f'{self.path} QUARTUS FILES CREATED')

    def compile_verilog(self):
        os.system(f'quartus_map verilog/{self.base_name}/{self.base_name}')
        os.system(f'quartus_fit verilog/{self.base_name}/{self.base_name}')
        os.system(f'quartus_sta verilog/{self.base_name}/{self.base_name}')
        os.system(f'quartus_eda verilog/{self.base_name}/{self.base_name}')
