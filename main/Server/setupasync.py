from setuptools import setup, Extension

setup(
    name='RSAasyncEncryption',
    ext_modules=[
        Extension(
            'RSAEncryption',
            ['asyncClass.cpp'],
            include_dirs=[r'/usr/local/lib/python3.10/site-packages/pybind11/include'],
            extra_compile_args=['-std=c++17','-lpython3.10'],
        ),
    ],
    zip_safe=False,
)