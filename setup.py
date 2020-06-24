import setuptools
import os

with open('requirements.txt') as f:
    reqs = f.readlines()

    
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths
package_data = package_files('src')

setuptools.setup(
    name="stlab",
    package_dir={'stlab': 'src'},
    packages= ['stlab'],
    install_requires = reqs,
    include_package_data=True,
    package_data={'stlab': package_data},
)