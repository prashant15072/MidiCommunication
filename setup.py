import sys
from cx_Freeze import setup, Executable


base=None
if (sys.platform=='win32'):
    base='Win32GUI'

executables=[
    Executable('Scripts\SendData.py',base=base)
]


setup(
    name='BTP',
    version='0.1',
    packages=['Scripts'],
    url='',
    license='',
    author='Prashant',
    author_email='',
    description='',
    executables=executables
)
