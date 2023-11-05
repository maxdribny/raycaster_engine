# build.py

import subprocess

# Build flags
FLAGS = {
    'VERSION': '0.0.1'
}

print(f'Building version {FLAGS["VERSION"]}')

command = 'pyinstaller'
params = ['--onefile', '--log-level', 'TRACE', 'main.py']

subprocess.run([command] + params)
