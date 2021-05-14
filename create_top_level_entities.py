import os


benchmark = str(input('benchmark: '))

n_inputs = int()
n_outputs = int()

with open(f'../temp/{benchmark}.pla', 'r') as fin:
    for line in fin.readlines():
        if '.i ' in line:
            n_inputs = int(line.split()[1])
        elif '.o ' in line:
            n_outputs = int(line.split()[1])

for method in ['direct_verilog_synthesis', 'abc_optimization_script', 'decision_tree_training_for_exact_circuits']:
    in_out_format = list()
    with open(f'{method}/{benchmark}/{benchmark}_out_0.v', 'r') as fin:
        for line in fin.readlines():
            if 'input ' in line and ' x' in line:
                in_out_format = ['x', 'z']
            elif 'input ' in line and ' pi' in line:
                in_out_format = ['pi', 'po']

    with open(f'{method}/{benchmark}/{benchmark}.v', 'w') as fout:
        print(f'module {benchmark} (', file=fout)

        print('\t', ', '.join([f'x{i:02d}' for i in range(n_inputs)]), ',', file=fout)
        print('\t', ', '.join([f'z{i:02d}' for i in range(n_outputs)]), ');\n', file=fout)
    
        print('\tinput ', ', '.join([f'x{i:02d}' for i in range(n_inputs)]), ';', file=fout)
        print('\toutput ', ', '.join([f'z{i:02d}' for i in range(n_outputs)]), ';\n', file=fout)
    
        for i in range(n_outputs):
            print(f'\t{benchmark}_out_{i} {benchmark}_o{i} (', file=fout)

            print('\t\t', ', '.join([f'.{in_out_format[0]}{j:02d}(x{j:02d})' for j in range(n_inputs)]), ',', file=fout)
            print(f'.{in_out_format[1]}0(z{i})', ');\n', file=fout)

        print('endmodule', file=fout)

