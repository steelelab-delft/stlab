import setuptools
with open('requirements.txt') as f:
    reqs = f.readlines()

setuptools.setup(
    name="stlab",
    package_dir={'stlab': 'src'},
    packages= ['stlab'],
    install_requires = reqs,
)