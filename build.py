# build.py

import subprocess

# Build flags
FLAGS = {
    'VERSION': '0.0.3'
}

print(f'Building version {FLAGS["VERSION"]}')

output_name = f'Raycaster_v{FLAGS["VERSION"]}'

command = 'pyinstaller'
params = ['--log-level', 'TRACE', '--noconfirm', f'--name={output_name}', 'main.py']

subprocess.run([command] + params)
