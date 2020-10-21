import tree_maker
import eqn_file_maker
from c50_files import make_c50_files
import clear


def main():
    clear

    make_c50_files.MakeC50Files().run_make_files()

    tree_maker.TreeMaker('c50_files/files').make_tree()

    eqn_file_maker.EqnFileMaker('pos').make_aig()
    eqn_file_maker.EqnFileMaker('sop').make_aig()


if __name__ == '__main__':
    main()
