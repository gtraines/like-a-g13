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
    url='https://github.com/gtraines/like-a-g13',

    packages=['LikeAG13'],
    package_data={'LikeAG13': ['*.h', '*.pxd']},
    #packages=setuptools.find_packages(),

    license='MIT',
    install_requires=open("requirements.txt").readlines(),
    include_package_data=True,
    ext_modules=cythonize('LikeAG13/**/*.pyx', compiler_directives={
        'language_level': '3',
        'c_string_type': 'unicode',
        'c_string_encoding': 'ascii'}),
    zip_safe=False
)
