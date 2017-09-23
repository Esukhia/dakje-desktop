from setuptools import find_packages, setup

EXCLUDE_FROM_PACKAGES = []

setup(
    name='RDRPOSTagger',
    version='1.0',
    url='https://github.com/nuwainfo/RDRPOSTagger',
    description=('Modified version for Tibetant Editor'),
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    zip_safe=False,
)
