import tree_maker
import eqn_file_maker
from c50_files import make_c50_files
import clear
import os


def main():
    clear

    make_c50_files.MakeC50Files().run_make_files()

    tree_maker.TreeMaker('c50_files/files').make_tree()

    for path in os.listdir('trees'):
        print(path)
        eqn_file_maker.EqnFileMaker(path).make_aig()


if __name__ == '__main__':
    main()
