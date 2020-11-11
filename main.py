import tree_maker
import eqn_file_maker
from c50_files import make_c50_files
import clear
import os


def main():
    initialize()

    make_c50_files.MakeC50Files().run_make_files()

    tree_maker.TreeMaker('c50_files/files').make_tree()

    for path in os.listdir('trees'):
        print(path)
        eqn_file_maker.EqnFileMaker(path).make_aig()


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

    clear


if __name__ == '__main__':
    main()
