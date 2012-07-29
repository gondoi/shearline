from setuptools import setup, find_packages

python_libraries = ['boto', 'python-cloudfiles']

setup(
    name='shearline',
    packages=[],
    entry_points={
        'console_scripts': [
            'shearline = shearline:main',
        ],
    },
    version='1.0',
    install_requires=python_libraries,
    license='GPLv2',
    description='S3 bucket to Cloud Files Container migration tool'
)
