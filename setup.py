import setuptools
with open('requirements.txt') as f:
    reqs = f.readlines()

# # Remove links to github repos
# # these have to be added manually
# reqs = [ r for r in reqs if "github" not in r ]

setuptools.setup(
    name="stlab",
    package_dir={'stlab': 'src'},
    packages= ['stlab'],
    install_requires = reqs,
    # dependency_links=['git+git://github.com/steelelab-delft/stlabutils/tarball/master']
)