from setuptools import setup, find_packages

setup(
    name='flux-certify',
    version='0.1.0',
    description='Compile FLUX-C guard constraints and generate proof certificates',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='SuperInstance',
    author_email='cocapn@example.com',
    url='https://github.com/SuperInstance/flux-certify',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires='>=3.8',
    install_requires=['click>=8.0'],
    entry_points={
        'console_scripts': ['flux-certify=flux_certify.cli:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Compilers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],
)
