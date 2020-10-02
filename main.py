import tree_maker
import eqn_file_maker
from c50_files import make_c50_files
import clear


def main():
    clear

    make_c50_files.MakeC50Files().run_make_files()

    tree_maker.TreeMaker('c50_files/files').make_tree()

    eqn_file_maker.EqnFileMaker('pos').make_eqn_files()
    eqn_file_maker.EqnFileMaker('sop').make_eqn_files()

    # eqn_file_maker.EqnFileMaker('sop').generate_logic('table3_out_8.tree.txt', 'table3_out_8.eqn')


if __name__ == '__main__':
    main()
