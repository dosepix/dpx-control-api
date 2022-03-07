import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='dpx_control_api',
    version='0.1',
    description='API for DPX control software',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Sebastian Schmidt',
    author_email='schm.seb@gmail.com',
    url="https://github.com/dosepix/dpx-control-api",
    project_urls={
        "Bug Tracker": "https://github.com/dosepix/dpx-control-api/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license='GNU GPLv3',
    packages=['dpx_control_api'],
    entry_points={
        'console_scripts' : [
            'dpx_control_api = dpx_control_api.__init__:main',
        ]
    },
    install_requires=[
        'flask',
        'pandas',
        'numpy',
        'dpx_control'
    ]
)
