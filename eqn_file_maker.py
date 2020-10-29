import os


class EqnFileMaker(object):
    def __init__(self, path):
        self.path = path

    def make_aig(self):
        self.make_eqn_file()
        self.make_aig_from_eqn()
        self.extract_data()

    def make_eqn_file(self):
        if '.tree' in self.path:
            input_path = str(f'trees/{self.path}')
            output_path = str(f'sop/{self.path.replace("tree.txt", "eqn")}')
            self.generate_logic(input_path, output_path)

        remove = False
        with open(output_path) as fin:
            lines = fin.readlines()
            if 'f1 = ;' in lines[2]:
                remove = True
        if remove:
            os.system(f'rm {output_path}')

        self.path = self.path.replace('tree.txt', 'eqn')

    def generate_logic(self, input_path, output_path):
        expression = ''
        sum = []
        n_attributes = 0
        prev_line = ''
        with open(input_path) as fin:
            for line in fin.readlines():
                if 'cases (' in line:
                    aux1 = line.find('(')
                    aux2 = line.find(')')
                    temp = line[aux1 + 1:aux2]
                    n_attributes = temp.split(' ')[0]

                if 'X' in line:
                    n = int(len(line.split('X')[0]) / 4)
                    n_prev = int(len(prev_line.split('X')[0]) / 4)

                    if ':' not in line:
                        break
                    if n <= n_prev:
                        if prev_line.split(' (')[0][-1] == '1':
                            expression += '+' + '*'.join(element for element in sum)
                            for i in range(n_prev - n + 1):
                                sum.pop()
                        elif len(sum):
                            sum.pop()
                    aux = line.replace(':', '').replace('.', '').replace(' ', '').split('=')
                    if aux[1][0] == '0':
                        sum.append('!' + aux[0])
                    else:
                        sum.append(aux[0])

                prev_line = line
        expression = expression[1:]

        with open(output_path, 'w') as fout:
            header = 'INORDER ='
            for i in range(int(n_attributes) - 1):
                header += ' X' + str(i)
            header += ';\nOUTORDER = f1;\n'
            final_expression = header + 'f1 = ' + expression + ';'
            print(final_expression, file=fout)

    @staticmethod
    def make_aig_from_pla(dir_path):
        for path in os.listdir(dir_path):
            if '.eqn' in path:
                new_file = str('espresso_script_automation/reduced_benchmarks_aig/' + path[:4] + '.train.aig')
                script = str('read_pla ' + dir_path + path + '\nstrash\nwrite_aiger ' + new_file + '\n&read ' +
                             new_file + '; &ps; &mltest Benchmarks/' + path[:4] + '.valid.pla')
                script_file = open('pla_script.scr', 'w+')
                script_file.write(script)
                script_file.close()

                mltest_result = open('mltest_result.txt', 'w+')
                mltest_result.truncate(0)
                mltest_result.close()
                os.system('./abc -c \'source pla_script.scr\' >> espresso_script_automation/mltest_result.txt')

    def make_aig_from_eqn(self):
        if '.eqn' in self.path:
            with open('temp/make_aig_from_eqn_script', 'w') as fout:
                print(f'read_eqn sop/{self.path}', file=fout)
                print('strash', file=fout)
                print(f'write_aiger sop/aig/{self.path.replace("eqn", "aig")}', file=fout)
            os.system('./abc -F temp/make_aig_from_eqn_script')
            self.path = self.path.replace('eqn', 'aig')

    def extract_data(self):
        with open('temp/mltest_script', 'w') as fout:
            output_number = ''
            if self.path[-5].isnumeric():
                if self.path[-6].isnumeric():
                    output_number = self.path[-6] + self.path[-5]
                else:
                    output_number = self.path[-5]
            print(f'&r sop/aig/{self.path}; &ps; &mltest temp/temp_out_{output_number}.pla', file=fout)

        file = open('temp/mltest_results', 'w')
        file.close()
        os.system('./abc -F temp/mltest_script >> temp/mltest_results')

        table_results = []

        try:
            with open(f'sop_table_results', 'r') as fin:
                table_results = fin.readlines()
        except Exception as e:
            print(e)

        try:
            with open(f'sop_table_results', 'w') as fout, open('temp/mltest_results', 'r') as fin:
                mltest_lines = fin.readlines()
                try:
                    ands = mltest_lines[3].split()[8][:-4]
                    levs = mltest_lines[3].split()[11][:-4]
                    acc = mltest_lines[5].split()[9].replace('(', '')
                    if acc == '':
                        acc = acc = mltest_lines[5].split()[10]
                    results = f'{self.path}\t{ands}\t{levs}\t{acc}'
                    table_results.append(results + '\n')
                except Exception as e:
                    print(e)
                finally:
                    fout.writelines(table_results)
        except Exception as e:
            print(e)
