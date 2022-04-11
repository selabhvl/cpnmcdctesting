import setuptools
import os

if __name__ == '__main__':
    with open("README.md", "r") as fh:
        long_description = fh.read()

    # We now define the CPNParser version number in CPNParser/__init__.py
    __version__ = 'unknown'
    for line in open('CPNParser/__init__.py'):
        if (line.startswith('__version__')):
            exec (line.strip('. '))

    setuptools.setup(
        name="CPNParser",
        version=__version__,
        author="J. Ignacio Requeno",
        author_email='jose.ignacio.requeno.jarabo@hvl.no',
        description='CPNParser is a parser for CPNTools for ' \
                    'Python 2.7, 3.4 or newer',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/selabhvl/cpnmcdctesting/tree/master/python/CPNParser',
        install_requires=[
            'ply>=3.11'
        ],
        #packages_dir={'': 'CPNParser'},
        #packages=setuptools.find_packages(exclude=['CPNParser._py3k', 'tests']),
        packages=setuptools.find_packages(),
        classifiers=(
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.4",
            "License :: GNU GPL",
            "Operating System :: OS Independent",
        ),
        use_2to3=True,
        test_suite=os.path.dirname(__file__) + '.tests',
        #convert_2to3_doctests=['src/your/module/README.txt'],
        #use_2to3_fixers=['your.fixers'],
        #use_2to3_exclude_fixers=['lib2to3.fixes.fix_import'],
        #license='GPL',
    )
