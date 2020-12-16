import tree_maker
import run_all
from c50_files import make_c50_files
import os


def main():
    initialize()

    errors = make_c50_files.MakeC50Files().run_make_files()

    tree_maker.TreeMaker('c50_files/files').make_tree()

    for path in os.listdir('trees'):
        print(path)
        os.system('rm temp/*.pla')
        try:
            make_c50_files.MakeC50Files().split_outputs(f'{path.split("_")[0]}.pla')
            run_all.RunAll(path).make_aig()
        except Exception as e:
            errors.append((path, e))

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
    if not os.path.exists('sop/aig'):
        os.mkdir('sop/aig')

    clear()
    open('sop_table_results.csv', 'x').close()


def clear():
    os.system('rm c50_files/files/* trees/* temp/* pos/* pos/aig/* sop/* sop/aig/* *_table_results nohup* *results*')


if __name__ == '__main__':
    main()
