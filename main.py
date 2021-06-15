import os
import run_all
import create_top_level_entities
import numpy as np

benchmark_dir = 'Benchmarks'

def main():
    initialize()

    errors = []
    graphic_data = []

    for path in os.listdir('Benchmarks'):
        if '.pla' not in path:
            continue
        
        if path[0].isnumeric():
            os.system(f'mv Benchmarks/{path} Benchmarks/ls_{path}')
            path = f'ls_{path}'
        if '-' in path:
            os.system(f'mv Benchmarks/{path} Benchmarks/{path.replace("-", "_")}')
            path = path.replace('-', '_')
        
        original_base_name = path.replace('.pla', '')
        os.mkdir(f'verilog/{original_base_name}')
        
        try:
            split_and_collapse(path)
        except Exception as e:
            print(e)
            continue

        x, y = np.loadtxt(f'temp/{path}', dtype='str', comments=".", skiprows=1, unpack=True)
        x = [list(_x) for _x in x]
        x = np.asarray(x).astype('uint8')
        y = [list(_y) for _y in y]
        y = np.asarray(y).astype('uint8')

        feature_names = list(map(str, list(range(x.shape[1]))))

        base_name = str()

        for i in range(y.shape[1]):
            try:
                base_name = original_base_name + '_out_' + str(i)

                acc = run_all.RunAll(base_name, x, y[:, i], feature_names).run()

                graphic_data.append((base_name, acc))
            except Exception as e:
                errors.append((base_name, e))
        try:
            create_top_level_entities.create_top_level_entity(original_base_name)
            run_all.RunAll(original_base_name).compile_verilog()
            run_all.RunAll(original_base_name).extract_synthesis_data()
        except Exception as e:
            print(e)

        os.system('rm -f temp/*.pla')

    open('errors.csv', 'x').close()
    errors_output = open('errors.csv', 'w')
    print('errors:')
    for e in errors:
        print(e)
        print(f'{e[0]}, {e[1]}', file=errors_output)
    errors_output.close()


def initialize():
    if not os.path.exists('temp'):
        os.mkdir('temp')
    if not os.path.exists('trees'):
        os.mkdir('trees')
    if not os.path.exists('sop'):
        os.mkdir('sop')
    if not os.path.exists('aig'):
        os.mkdir('aig')
    if not os.path.exists('verilog'):
        os.mkdir('verilog')
    if not os.path.exists('mltest'):
        os.mkdir('mltest')

    clear()
    open('aig_table_results.csv', 'x').close()


def clear():
    os.system('rm -f c50_files/files/* trees/* temp/* pos/* pos/aig/* sop/* aig/* nohup* *.csv')
    os.system('rm -f -r verilog/* mltest/*')


def split_and_collapse(_path):
    try:
        with open(f'Benchmarks/{_path}', 'r') as fin:
            for line in fin.readlines():
                if '.i' in line:
                    if int(line.split(' ')[1]) > 16:
                        os.system(f'rm -rf verilog/{_path.replace(".pla", "")}')
                        raise Exception('Numero de inputs superior a 16')
                    else:
                        break
        with open('temp/collapse_script', 'w') as fout:
            print(f'read_pla Benchmarks/' + _path + f'; collapse; write_pla -m temp/{_path}', file=fout)
        os.system('./abc -F temp/collapse_script')

        number_of_outputs = 0
        with open(f'temp/{_path}', 'r') as fin:
            temp_pla = fin.read()
            for _line in temp_pla.splitlines():
                if '.o' in _line:
                    number_of_outputs = int(_line.split()[1])
                    break

        for _i in range(number_of_outputs):
            with open(f'temp/{_path.replace(".pla", "")}_out_' + str(_i) + '.pla', 'w') as fout:
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
        raise e


if __name__ == '__main__':
    main()

