1#
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import find_packages

from sys import platform as _platform
import sys
import glob
import os


from distutils.core import setup
from distutils.extension import Extension
from distutils.util import get_platform
from glob import glob

# monkey-patch for parallel compilation
import multiprocessing
import multiprocessing.pool

my_data_files=[]


def parallelCCompile(self,
                     sources,
                     output_dir=None,
                     macros=None,
                     include_dirs=None,
                     debug=0,
                     extra_preargs=None,
                     extra_postargs=None,
                     depends=None):
    # those lines are copied from distutils.ccompiler.CCompiler directly
    macros, objects, extra_postargs, pp_opts, build = self._setup_compile(
        output_dir, macros, include_dirs, sources, depends, extra_postargs)
    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
    # parallel code
    N = 2 * multiprocessing.cpu_count()  # number of parallel compilations
    try:
        # On Unix-like platforms attempt to obtain the total memory in the
        # machine and limit the number of parallel jobs to the number of Gbs
        # of RAM (to avoid killing smaller platforms like the Pi)
        mem = os.sysconf('SC_PHYS_PAGES') * os.sysconf('SC_PAGE_SIZE')  # bytes
    except (AttributeError, ValueError):
        # Couldn't query RAM; don't limit parallelism (it's probably a well
        # equipped Windows / Mac OS X box)
        pass
    else:
        mem = max(1, int(round(mem / 1024 ** 3)))  # convert to Gb
        N = min(mem, N)

    def _single_compile(obj):
        try:
            src, ext = build[obj]
        except KeyError:
            return
        newcc_args = cc_args
        if _platform == "darwin":
            if src.endswith('.cpp') or src.endswith('.cc'):
                newcc_args = cc_args + ["-mmacosx-version-min=10.15", "-std=c++17", "-stdlib=libc++"]
        self._compile(obj, src, ext, newcc_args, extra_postargs, pp_opts)

    # convert to list, imap is evaluated on-demand
    pool = multiprocessing.pool.ThreadPool(N)
    list(pool.imap(_single_compile, objects))
    return objects


import distutils.ccompiler

distutils.ccompiler.CCompiler.compile = parallelCCompile

# see http://stackoverflow.com/a/8719066/295157
import os

platform = get_platform()
print(platform)

CXX_FLAGS = ''
CXX_FLAGS += '-fpermissive '



# libraries += [current_python]

libraries = []
include_dirs = ['third_party/pybind11/include',]

try:
    import numpy

    NP_DIRS = [numpy.get_include()]
except:
    print("numpy is disabled.")
else:
    print("numpy is enabled.")
    for d in NP_DIRS:
        print("numpy_include_dirs = %s" % d)
    include_dirs += NP_DIRS

sources = ["pybind11_test.cc",]



if _platform == "linux" or _platform == "linux2":
    print("linux")
    libraries = ['dl']
    CXX_FLAGS += '-D_LINUX '
    
elif _platform == "win32":
    print("win32!")
    libraries = ['User32', 'kernel32', ]
    CXX_FLAGS += '-DWIN32 '
    CXX_FLAGS += '/std:c++17 '
    
elif _platform == "darwin":
    print("darwin!")
    os.environ['LDFLAGS'] = '-framework Cocoa -mmacosx-version-min=10.15 '
    CXX_FLAGS += '-D_DARWIN '
    CXX_FLAGS += '-mmacosx-version-min=10.15 '
    
else:
    print("unknown platform!")

setup_py_dir = os.path.dirname(os.path.realpath(__file__))

need_files = []


extensions = []

CXX_FLAGS_TEST = CXX_FLAGS 

pybind11_test_ext = Extension(
    "pybind11_test",
    sources=sources,
    libraries=libraries,
    extra_compile_args=CXX_FLAGS_TEST.split(),
    include_dirs=include_dirs + ["."])

extensions.append(pybind11_test_ext)




setup(
    name='pybind11_test',
    version='0.0.1',
    description=
    'Python bindings using pybind11 test',
    long_description=
    'Python bindings',
    url='https://github.com/erwincoumans/pybind11_issue',
    author='Erwin Coumans',
    author_email='erwincoumans@google.com',
    license='Apache License 2.0',
    platforms='any',
    keywords=[
        "pybind11"
    ],
    install_requires=[
        'numpy',
    ],
    ext_modules=extensions,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: zlib/libpng License',
        'Operating System :: Microsoft :: Windows', 'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS', 'Intended Audience :: Science/Research',
        "Programming Language :: Python", 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4', 'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6', 'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8', 'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Framework :: Robot Framework'
    ],
)
