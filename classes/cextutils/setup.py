from distutils.core import setup
from Cython.Build import cythonize

setup(
  name='cextutils',
  ext_modules=cythonize("utils.pyx"),
)