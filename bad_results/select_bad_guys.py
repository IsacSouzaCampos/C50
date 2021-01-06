import os


def split_outputs(_path):
    try:
        with open(f'../Benchmarks/{_path}', 'r') as fin:
            for line in fin.readlines():
                if '.i' in line:
                    if int(line.split(' ')[1]) > 16:
                        raise Exception('Numero de inputs superior a 16')
                    else:
                        break
        with open('../temp/collapse_script', 'w') as fout:
            print('read_pla ../Benchmarks/' + _path + '; collapse; write_pla -m ../temp/temp.pla', file=fout)
        os.system('.././abc -F ../temp/collapse_script')

        number_of_outputs = 0
        with open('../temp/temp.pla', 'r') as fin:
            temp_pla = fin.read()
            for _line in temp_pla.splitlines():
                if '.o' in _line:
                    number_of_outputs = int(_line.split()[1])
                    break

        for _i in range(number_of_outputs):
            with open('../temp/temp_out_' + str(_i) + '.pla', 'w') as fout:
                for _line in temp_pla.splitlines():
                    if _line[0] not in ['0', '1']:
                        if '#' in _line or '.e' in _line:
                            continue
                        print(_line, file=fout)
                    else:
                        _lines = _line.split()
                        print(_lines[0] + ' ' + _lines[1][_i], file=fout)
                print('.e', file=fout)

        return number_of_outputs

    except Exception as e:
        print(e)


try:
    os.system('rm bad_PLAs/* bad_AIGs/* bad_EQNs/*')
except Exception as e:
    print(e)

bad_guys = []
with open('results.csv', 'r') as fin:
    for line in fin.readlines():
        columns = line.split(',')
        if float(columns[-1]) < 75:
            bad_guys.append(columns[0])

bad_guys = sorted(bad_guys)

print()

current = bad_guys[0].split('_')[0]
outputs = []
bad_outputs = []
cont = 0
for i in range(len(bad_guys)):
    s = bad_guys[i].split('_')
    if s[0] == current:
        outputs.append(s[2].replace('.aig', ''))
    else:
        cont += len(outputs)
        bad_outputs.append((current, list(outputs)))
        print((current, outputs))
        outputs.clear()
        current = s[0]
        outputs.append(s[2].replace('.aig', ''))
bad_outputs.append((current, list(outputs)))

for bo in bad_outputs:
    os.system('rm ../temp/*.pla')
    for path in os.listdir('../Benchmarks'):
        if bo[0] == path.split('.')[0]:
            split_outputs(path)
            for n in bo[1]:
                for f in os.listdir('../temp'):
                    if f'_out_{n}.pla' in f:
                        os.system(f'cp ../temp/{f} bad_PLAs/{bo[0]}_out_{n}.pla')
                        os.system(f'cp AIGs/{bo[0]}_out_{n}.aig bad_AIGs')
                        os.system(f'cp EQNs/{bo[0]}_out_{n}.eqn bad_EQNs')
                        os.system(f'cp TREEs/{bo[0]}_out_{n}.tree bad_TREEs')

for tree in os.listdir('bad_TREEs'):
    if tree.replace('tree', 'aig') not in os.listdir('bad_AIGs'):
        os.system(f'rm bad_TREEs/{tree}')

with open('bad_outputs.csv', 'w') as fout:
    for bo in bad_outputs:
        print(f'{bo[0]},{",".join([t for t in bo[1]])}', file=fout)

print('\n' + str(cont))
