#!D:\Python\howdoi-master\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'howdoi==1.1.13','console_scripts','howdoi'
__requires__ = 'howdoi==1.1.13'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('howdoi==1.1.13', 'console_scripts', 'howdoi')()
    )
