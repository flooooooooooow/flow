#!/usr/bin/env python3
from setuptools import setup, Extension

my_math_ext = Extension(
    'my_math',
    sources=['my_math_ext.c'],
    extra_compile_args=['-O2', '-Wall'],
)

setup(
    name='my_math',
    version='2.0.0',
    description='Flow-generated Python extension',
    ext_modules=[my_math_ext],
    python_requires='>=3.8',
)
