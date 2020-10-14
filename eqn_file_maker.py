import os


class EqnFileMaker(object):
    def __init__(self, eqn_type='pos'):
        # self.benchmark_type = benchmark_type
        self.eqn_type = eqn_type

    def make_eqn_files(self):
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

            self.make_aig_from_eqn(path.replace('tree.txt', 'eqn'))

    def generate_logic(self, input_path, output_path):
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

    # def unite_eqn(self, ex):  # file_type = 'original' | 'non_redundant'
    #     header = ''
    #     sop = ''
    #     pos = ''
    #
    #     try:
    #         with open('sop/' + self.benchmark_type + '/' + ex + '.train.eqn') as file:
    #             temp = file.read().split('f1 = ')
    #             header += temp[0]
    #             sop += temp[1]
    #         with open('pos/' + self.benchmark_type + '/' + ex + '.train.eqn') as file:
    #             pos += file.read().split('f1 = ')[1]
    #
    #         result = ''
    #         if sop == '1;':
    #             result += '1;'
    #         elif sop == '0;':
    #             result += '0;'
    #         else:
    #             result += sop.replace(';', '') + '+' + pos
    #
    #         # print('file_type + '_sop_pos/' + path[:4] + '.train.eqn')
    #         output_file = open('sop_pos/' + self.benchmark_type + '/' + ex + '.train.eqn', 'w+')
    #         output_file.write(header + 'f1 = ' + result)
    #     except Exception as e:
    #         print(e)
    #     else:
    #         self.apply_multiplexer(header, sop.replace(';', ''), pos.replace(';', ''), ex)

    # def apply_multiplexer(self, header, sop, pos, ex):
    #     default_class = ''
    #     with open('trees/' + self.benchmark_type + '/' + ex + '.tree.txt') as file:
    #         for line in file:
    #             if 'Default class' in line:
    #                 default_class += line.split(': ')[1][:1]
    #
    #     # nand1 !(sop * pos)
    #     nand1 = str('!(' + sop + ' * ' + pos + ')')
    #     # nand2 !(sop * nand1)
    #     nand2 = str('!(' + sop + ' * ' + nand1 + ')')
    #     # nand3 !(nand1 * pos)
    #     nand3 = str('!(' + nand1 + ' * ' + pos + ')')
    #     # nand4 !(nand2 * nand3)
    #     nand4 = str('!(' + nand2 + ' * ' + nand3 + ')')
    #
    #     # mux_and1  (sop * !nand4)
    #     mux_and1 = str('(' + sop + ' * !' + nand4 + ')')
    #     # mux_and2  (default_class * nand4)
    #     mux_and2 = str('(' + default_class + ' * ' + nand4 + ')')
    #     # result    !(!mux_and1 * !mux_and2)
    #     result = str('!(!' + mux_and1 + ' * !' + mux_and2 + ')')
    #
    #     output_file = open('sop_pos_mux/' + self.benchmark_type + '/' + ex + '.train.eqn', 'w+')
    #     output_file.write(header + 'f1 = ' + result.replace('!!', '') + ';')
    #     output_file.close()

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
            self.extract_data(path.replace('eqn', 'aig'))

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
