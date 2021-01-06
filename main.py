import tree_maker
import run_all
from c50_files import make_c50_files
import os


def main():
    initialize()

    errors = []
    for path in os.listdir('Benchmarks'):
        make_c50_files_results = make_c50_files.MakeC50Files().run_make_files(path)
        errors.append((path, make_c50_files_results[0]))
        number_of_outputs = make_c50_files_results[1]
        benchmarck_name = path.replace('.pla', '')

        tree_maker.TreeMaker().make_tree(benchmarck_name, number_of_outputs)

        for tree in os.listdir('trees'):
            try:
                print(f'tree = {tree}')
                run_all.RunAll(tree).run()
            except Exception as e:
                errors.append((tree, e))

    open('errors.csv', 'x').close()
    errors_output = open('errors.csv', 'w')
    print('errors:')
    for e in errors:
        print(e)
        print(f'{e[0]}, {e[1]}', file=errors_output)
    errors_output.close()


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

    clear()
    open('sop_table_results.csv', 'x').close()


def clear():
    os.system('rm c50_files/files/* trees/* temp/* pos/* pos/aig/* sop/* aig/* verilog/* nohup* *.csv')


if __name__ == '__main__':
    main()
