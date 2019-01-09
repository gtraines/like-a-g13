#!/usr/bin/env python

# Per Cython docs:
# import setuptools before Cython as setuptools may replace the Extension class
# in distutils. Otherwise, both might disagree about the class to use here
import setuptools
from Cython.Build import cythonize

setuptools.setup(
    name='like-a-g13',
    version='0.0.1',

    description='G13 MFD and control mapping library',
    url='https://github.com/gtraines/g13',

    packages=setuptools.find_packages(),

    license='MIT',

    install_requires=open("requirements.txt").readlines(),
)



"""
    See http://cython.readthedocs.io/en/latest/src/reference/compilation.html
    'Note that when using setuptools, you should .'
"""

setup(
    name='cy_package',
    packages=['cy_package'],
    package_data={'cy_package': ['*.h', '*.pxd']},
    include_package_data=True,
    ext_modules=cythonize('cy_package/**/*.pyx', compiler_directives={
        'language_level': '3',
        'c_string_type': 'unicode',
        'c_string_encoding': 'ascii'}),
    zip_safe=False)