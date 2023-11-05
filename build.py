# build.py

import subprocess

# Build flags
FLAGS = {
    'IS_BUILD_VERSION': False,
    'VERSION': '0.0.1'
}

print(f'Building version {FLAGS["VERSION"]}')
print(f'FLAGS = {FLAGS}')

# Check if IS_BUILD_VERSION is set to False
if FLAGS['IS_BUILD_VERSION']:
    command = 'pyinstaller'
    params = ['--onefile', '--log-level', 'TRACE', 'main.py']

    subprocess.run([command] + params)
else:
    print(f'Not building because IS_BUILD_VERSION is set to {FLAGS["IS_BUILD_VERSION"]}')
