import TreeMaker
import EqnFileMaker
from c50_files import make_c50_files
import clear


def main():
    clear
    make_c50_files.MakeC50Files().run_make_files()
    TreeMaker.TreeMaker('c50_files/files').make_tree()
    EqnFileMaker.EqnFileMaker('pos').make_eqn_files()
    EqnFileMaker.EqnFileMaker('sop').make_eqn_files()


if __name__ == '__main__':
    main()
