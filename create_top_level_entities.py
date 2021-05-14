def create_top_level_entity(benchmark):
    n_inputs = int()
    n_outputs = int()

    # get benchmark's number of inputs and outputs
    with open(f'temp/{benchmark}.pla', 'r') as fin:
        for line in fin.readlines():
            if '.i ' in line:
                n_inputs = int(line.split()[1])
            elif '.o ' in line:
                n_outputs = int(line.split()[1])

    in_out_format = list()
    with open(f'verilog/{benchmark}/{benchmark}_out_0.v', 'r') as fin:
        for line in fin.readlines():
            if 'input ' in line and ' x' in line:
                in_out_format = ['x', 'z']
            elif 'input ' in line and ' pi' in line:
                in_out_format = ['pi', 'po']

    with open(f'verilog/{benchmark}/{benchmark}.v', 'w') as fout:
        print(f'module {benchmark} (', file=fout)

        if n_inputs < 11:
            inputs = ', '.join([f'x{i:01d}' for i in range(n_inputs)])
        else:
            inputs = ', '.join([f'x{i:02d}' for i in range(n_inputs)])
        if n_outputs < 11:
            outputs = ', '.join([f'z{i:01d}' for i in range(n_outputs)])
        else:
            outputs = ', '.join([f'z{i:02d}' for i in range(n_outputs)])

        print('\t', inputs, ',', file=fout)
        print('\t', outputs, ');\n', file=fout)

        print('\tinput ', inputs, ';', file=fout)
        print('\toutput ', outputs, ';\n', file=fout)

        for i in range(n_outputs):
            print(f'\t{benchmark}_out_{i} {benchmark}_o{i} (', file=fout)

            if n_inputs < 11:
                print('\t\t', ', '.join([f'.{in_out_format[0]}{j:01d}(x{j:01d})' for j in range(n_inputs)]), ',', file=fout)
            else:
                print('\t\t', ', '.join([f'.{in_out_format[0]}{j:02d}(x{j:02d})' for j in range(n_inputs)]), ',',
                      file=fout)
            print(f'.{in_out_format[1]}0(z{i})', ');\n', file=fout)

        print('endmodule', file=fout)
