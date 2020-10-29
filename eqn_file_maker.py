import os


class EqnFileMaker(object):
    def __init__(self, eqn_type='sop'):
        self.eqn_type = eqn_type

    def make_aig(self):
        eqn_paths = self.make_eqn_files()
        for path in eqn_paths:
            self.extract_data(self.make_aig_from_eqn(path))

    def make_eqn_files(self):
        paths = []
        for path in os.listdir('trees/'):
            if '.tree' in path:
                input_path = str(f'trees/{path}')
                output_path = str(f'{self.eqn_type}/{path.replace("tree.txt", "eqn")}')
                self.generate_logic(input_path, output_path)

            remove = False
            with open(output_path) as fin:
                lines = fin.readlines()
                if 'f1 = ;' in lines[2]:
                    remove = True
            if remove:
                os.system(f'rm {output_path}')

            paths.append(path.replace('tree.txt', 'eqn'))
        return paths

    def generate_logic_from_rules_tree(self, input_path, output_path):
        symbols = []
        if 'sop' in self.eqn_type:
            symbols.append('+')
            symbols.append('*')
            symbols.append('1')
        elif 'pos' in self.eqn_type:
            symbols.append('*')
            symbols.append('+')
            symbols.append('0')
        else:
            print('wrong eqn type')
            return

        header = ''
        logic_equation = ''
        inputs = []
        bits = []
        with open(input_path) as file:
            for line in file:
                if 'Read ' in line:
                    input_size = int(line.split(' ')[3][1:]) - 1
                    header += 'INORDER ='
                    for i in range(input_size):
                        header += ' x' + str(i)
                elif 'Rules:' in line:
                    break
            header += ';\nOUTORDER = f1;\nf1 = '
            for line in file:
                if 'X' in line and '%' not in line:
                    vec = line.split(' = ')
                    inputs.append(vec[0][1:].lower())
                    bits.append(vec[1])
                elif '->  class' in line:
                    if line[11] == symbols[2]:
                        logic_equation += '('
                        for i in range(len(inputs) - 1):
                            if int(bits[i]) != int(symbols[2]):
                                logic_equation += '!' + inputs[i] + symbols[1]
                            else:
                                logic_equation += inputs[i] + symbols[1]
                        if int(bits[len(bits) - 1]) != int(symbols[2]):
                            logic_equation += '!' + inputs[len(bits) - 1] + ')' + symbols[0]
                        else:
                            logic_equation += inputs[len(bits) - 1] + ')' + symbols[0]
                    inputs.clear()
                    bits.clear()

            # flag = False
            # if not logic_equation:  # empty string
            #     logic_equation += '1.'
            #     flag = True

            logic_equation = logic_equation[:len(logic_equation) - 1]
            logic_equation += ';'
            output_file = open(output_path, 'w+')
            output_file.write(header + logic_equation)
            output_file.close()

            # if flag:
            #     self.test_constant_outputs_accuracy(output_path)

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
                    n = line.count(':')
                    if n == 0:
                        break
                    if n <= len(sum):
                        if prev_line.split(' (')[0][-1] == '1':
                            expression += '+' + '*'.join(element for element in sum)
                        for i in range(n - len(sum) + 1):
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

    def make_aig_from_eqn(self, path):
        if '.eqn' in path:
            with open('temp/make_aig_from_eqn_script', 'w') as fout:
                print(f'read_eqn {self.eqn_type}/{path}', file=fout)
                print('strash', file=fout)
                print(f'write_aiger {self.eqn_type}/aig/{path.replace("eqn", "aig")}', file=fout)
            os.system('./abc -F temp/make_aig_from_eqn_script')
            return path.replace('eqn', 'aig')

    def extract_data(self, path):
        with open('temp/mltest_script', 'w') as fout:
            output_number = ''
            if path[-5].isnumeric():
                if path[-6].isnumeric():
                    output_number = path[-6] + path[-5]
                else:
                    output_number = path[-5]
            print(f'&r {self.eqn_type}/aig/{path}; &ps; &mltest temp/temp_out_{output_number}.pla', file=fout)

        file = open('temp/mltest_results', 'w')
        file.close()
        os.system('./abc -F temp/mltest_script >> temp/mltest_results')

        table_results = []

        try:
            with open(f'{self.eqn_type}_table_results', 'r') as fin:
                table_results = fin.readlines()
        except Exception as e:
            print(e)

        try:
            with open(f'{self.eqn_type}_table_results', 'w') as fout, open('temp/mltest_results', 'r') as fin:
                mltest_lines = fin.readlines()
                try:
                    ands = mltest_lines[3].split()[8][:-4]
                    levs = mltest_lines[3].split()[11][:-4]
                    acc = mltest_lines[5].split()[9].replace('(', '')
                    if acc == '':
                        acc = acc = mltest_lines[5].split()[10]
                    results = f'{path}\t{ands}\t{levs}\t{acc}'
                    table_results.append(results + '\n')
                except Exception as e:
                    print(e)
                finally:
                    fout.writelines(table_results)
        except Exception as e:
            print(e)
