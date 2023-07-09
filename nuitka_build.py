import glob
import os
import platform
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import main
from utils.config import Umi

SYSTEM = platform.system()
ARCH = platform.architecture()[0][:2]

APP_VERSION = Umi.ver
APP_NAME = Umi.pname
EXEC_NAME = "main"

PROJECT_DIR = Path(__file__).absolute().parent
SOURCE_DIR = Path('./')
BUILD_DIR = Path('build')

if not BUILD_DIR.exists():
    BUILD_DIR.mkdir()
OUTPUT_DIR = BUILD_DIR / f'{SYSTEM}-{ARCH}'
print(APP_VERSION)
RELEASE_DIR = Path('release') / APP_VERSION
print(RELEASE_DIR)
if not RELEASE_DIR.exists():
    os.makedirs(RELEASE_DIR, exist_ok=True)

# subprocess.call(['pip', 'install', '-U', 'nuitka'])
# subprocess.call(['pip', 'install', '-r', 'requirements.txt'])


def build():
    nuitka_cmd = [
        'python',
        '-m',
        'nuitka',
        '--show-progress',
        '--show-memory',
        '--standalone',
        '--include-data-dir=icon=icon',
        "--include-data-dir=PaddleOCR-json=PaddleOCR-json",
        "--include-data-files=PaddleOCR-json/*.dll=PaddleOCR-json/",
        '--plugin-enable=tk-inter',
        f'--output-dir={OUTPUT_DIR}'
    ]
    if platform.system() == 'Windows':
        nuitka_cmd.extend(
            (
                '--windows-disable-console',
                '--windows-icon-from-ico=icon/icon.ico',
            )
        )
    nuitka_cmd.append(f'{SOURCE_DIR}/{EXEC_NAME}.py')
    process = subprocess.run(nuitka_cmd, shell=True)
    if process.returncode != 0:
        raise ChildProcessError('Nuitka building failed.')
    print('Building done.')


def create_portable():
    file_list = glob.glob(f'{OUTPUT_DIR / APP_NAME}.dist/**', recursive=True)
    file_list.sort()
    portable_file = RELEASE_DIR / f'{APP_NAME}-{APP_VERSION}-Portable-{SYSTEM}-{ARCH}.zip'

    print('Creating portable package...')
    with ZipFile(portable_file, 'w', compression=ZIP_DEFLATED) as zf:
        for file in file_list:
            file = Path(file)
            name_in_zip = f'{APP_NAME}-{ARCH}/{"/".join(file.parts[3:])}'
            print(name_in_zip)
            if file.is_file():
                zf.write(file, name_in_zip)
    print('Creating portable package done.')


def update_iss():
    settings = {
        'APP_VERSION': APP_VERSION,
        'PROJECT_DIR': str(PROJECT_DIR),
        'OUTPUT_DIR': str(OUTPUT_DIR),
        'RELEASE_DIR': str(RELEASE_DIR),
        'ARCH': ARCH,
        'ARCH_MODE': 'ArchitecturesInstallIn64BitMode=x64' if ARCH == '64' else ''
    }

    iss_template = f'nuitka-setup-template.iss'
    iss_work = Path(BUILD_DIR) / f'{APP_NAME}-{ARCH}.iss'

    with open(iss_template) as template:
        iss_script = template.read()

    for key in settings:
        iss_script = iss_script.replace(f'%%{key}%%', settings.get(key))

    with open(iss_work, 'w') as iss:
        iss.write(iss_script)

    return iss_work


def check_iss():
    if ARCH == '64':
        program_files = os.environ.get('ProgramFiles(x86)')
    else:
        program_files = os.environ.get('ProgramFiles')
    iss_compiler = Path(program_files) / 'Inno Setup 6' / 'Compil32.exe'

    if iss_compiler.exists():
        return iss_compiler
    return None


def create_setup():
    iss_work = update_iss()
    iss_compiler = check_iss()
    if iss_compiler:
        print('Creating Windows Installer...', end='')
        compiler_cmd = [str(iss_compiler), '/cc', str(iss_work)]
        process = subprocess.run(compiler_cmd)
        if process.returncode != 0:
            raise ChildProcessError('Creating Windows installer failed.')
        print('done')


if __name__ == '__main__':
    build()
    create_portable()
    if SYSTEM == 'Windows':
        create_setup()
