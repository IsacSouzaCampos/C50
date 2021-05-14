import tree_maker
import run_all
from c50_files import make_c50_files
import os


def main():
    initialize()

    errors = []
    graphic_data = []

    benchmarck_dir = 'Benchmarks'
    for path in os.listdir(benchmarck_dir):
        if '.pla' not in path:
            continue
        if path[0].isnumeric():
            os.rename(f'{benchmarck_dir}/{path}', f'{benchmarck_dir}/c{path}')
            path = f'c{path}'
        if '-' in path:
            os.rename(f'{benchmarck_dir}/{path}', f'{benchmarck_dir}/{path.replace("-", "_")}')
            path = path.replace('-', '_')

        original_base_name = path.replace('.pla', '')
        os.mkdir(f'verilog/{original_base_name}')

        base_name = str()
        number_of_outputs = int()
        try:
            number_of_outputs = split_outputs(path)
        except Exception as e:
            errors.append((base_name, e))

        for i in range(number_of_outputs):
            try:
                base_name = original_base_name + '_out_' + str(i)

                make_c50_files_results = make_c50_files.MakeC50Files().run_make_files(base_name)
                errors.append((path, make_c50_files_results[0]))
                output_proportion = make_c50_files_results[1]

                # base_name = base_name + '_temp'

                # tree_maker.TreeMaker().make_tree(base_name)
                acc = run_all.RunAll(base_name).run()

                graphic_data.append((base_name, output_proportion, acc))
            except Exception as e:
                errors.append((base_name, e))

        os.system('rm temp/*.pla')

    open('errors.csv', 'x').close()
    errors_output = open('errors.csv', 'w')
    print('errors:')
    for e in errors:
        print(e)
        print(f'{e[0]}, {e[1]}', file=errors_output)
    errors_output.close()

    with open('graphic_data.csv', 'w') as fout:
        for data in graphic_data:
            print(f'{data[0]},{data[1]},{data[2]}', file=fout)


def initialize():
    if not os.path.exists('c50_files/files'):
        os.mkdir('c50_files/files')
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
    open('sop_table_results.csv', 'x').close()


def clear():
    os.system('rm c50_files/files/* trees/* temp/* pos/* pos/aig/* sop/* aig/* nohup* *.csv')
    os.system('rm -r verilog/* mltest/*')


def split_outputs(_path):
    try:
        with open(f'Benchmarks/{_path}', 'r') as fin:
            for line in fin.readlines():
                if '.i' in line:
                    if int(line.split(' ')[1]) > 16:
                        raise Exception('Numero de inputs superior a 16')
                    else:
                        break
        with open('temp/collapse_script', 'w') as fout:
            print('read_pla Benchmarks/' + _path + f'; collapse; write_pla -m temp/{_path}', file=fout)
        os.system('./abc -F temp/collapse_script')

        number_of_outputs = 0
        with open(f'temp/{_path}', 'r') as fin:
            temp_pla = fin.read()
            for _line in temp_pla.splitlines():
                if '.o' in _line:
                    number_of_outputs = int(_line.split()[1])
                    break

        for _i in range(number_of_outputs):
            with open(f'temp/{_path.replace(".pla", "")}_out_'+str(_i)+'.pla', 'w') as fout:
                for _line in temp_pla.splitlines():
                    if _line[0] not in ['0', '1']:
                        if '#' in _line or '.e' in _line:
                            continue
                        print(_line, file=fout)
                    else:
                        _lines = _line.split()
                        print(_lines[0]+' '+_lines[1][_i], file=fout)
                print('.e', file=fout)

        return number_of_outputs

    except Exception as e:
        raise e


if __name__ == '__main__':
    main()
