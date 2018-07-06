from __future__ import print_function
import shutil

from irods.core_file import temporary_core_file, CoreFile

def main():
    core = CoreFile()
    backupcorefilepath = core.filepath + "--jargon"
    shutil.copy(core.filepath, backupcorefilepath)

    core.add_rule('''acPreConnect(*OUT) { *OUT="CS_NEG_REFUSE"; }\n''')

if __name__ == '__main__':
    main()  
