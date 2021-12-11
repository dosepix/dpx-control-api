from setuptools import setup

setup(name='dpx_gui',
    version='0.1',
    description='DPX gui',
    author='Sebastian Schmidt',
    author_email='schm.seb@gmail.com',
    license='MIT',
    packages=['dpx_gui'],
    entry_points={
        'console_scripts' : [
            'dpx_gui = dpx_gui.dpx_gui:main',
        ]
    },
    install_requires=[
        'flask',
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
        'pyserial',
        'configparser',
        'tqdm',
        'dpx_control'
    ])
