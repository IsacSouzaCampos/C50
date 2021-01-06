import os


class RunAll(object):
    def __init__(self, path):
        self.path = path

    def run(self):
        try:
            self.make_eqn_file()
            self.make_aig_from_eqn()
            self.extract_data()
            self.make_verilog()

        except Exception as e:
            raise e

    def make_eqn_file(self):
        # print(f'make_eqn_file ({self.path})')
        try:
            output_path = ''
            if '.tree' in self.path:
                input_path = str(f'trees/{self.path}')
                output_path = str(f'sop/{self.path.replace("tree", "eqn")}')
                self.generate_logic(input_path, output_path)

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

    @staticmethod
    def generate_logic(input_path, output_path):
        # print(f'generate_logic ({input_path})')
        try:
            expression = ''
            s = []  # sum
            n_attributes = 0
            prev_line = ''
            with open(input_path) as fin:
                for line in fin.readlines():
                    if 'cases (' in line:
                        aux1 = line.find('(')
                        aux2 = line.find(')')
                        temp = line[aux1 + 1:aux2]
                        n_attributes = temp.split(' ')[0]

                    if len(line) > 1 and line[0] == ' ':
                        if line[1] == '0':
                            expression += '0'
                        elif line[1] == '1':
                            expression += '1'

                    if 'X' in line:
                        n = int(len(line.split('X')[0]) / 4)
                        n_prev = int(len(prev_line.split('X')[0]) / 4)

                        if ':' not in line:
                            break
                        if n <= n_prev:
                            if prev_line.split(' (')[0][-1] == '1':
                                expression += '+' + '*'.join(element for element in s)
                                for i in range(n_prev - n + 1):
                                    s.pop()
                            elif len(s):
                                s.pop()
                        aux = line.replace(':', '').replace('.', '').replace(' ', '').split('=')
                        if aux[1][0] == '0':
                            s.append('!' + aux[0])
                        else:
                            s.append(aux[0])

                    prev_line = line
            if len(expression) > 0 and expression[0] == '+':
                expression = expression[1:]

            with open(output_path, 'w') as fout:
                header = 'INORDER ='
                for i in range(int(n_attributes) - 1):
                    header += ' X' + str(i)
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

        file = open('temp/mltest_results.txt', 'w')
        file.close()
        os.system('./abc -F temp/mltest_script >> temp/mltest_results.txt')

        try:
            with open(f'sop_table_results.csv', 'r') as fin:
                table_results = fin.readlines()
        except Exception as e:
            raise Exception(f'Error 5: {e}')

        try:
            with open(f'sop_table_results.csv', 'w') as fout, open('temp/mltest_results.txt', 'r') as fin:
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
        # print(f'make_verilog ({self.path})')
        verilog_file = self.path.replace("aig", "v")
        with open('temp/make_verilog_script', 'w') as fout:
            print(f'read_aiger aig/{self.path}\n'
                  f'write_verilog verilog/{verilog_file}', file=fout)
        os.system('./abc -F temp/make_verilog_script')

        with open(f'verilog/{verilog_file}', 'r') as fin:
            verilog = fin.read()
            verilog.replace('\\aig/', '')

        with open(f'verilog/{verilog_file}', 'w') as fout:
            print(verilog, file=fout)
