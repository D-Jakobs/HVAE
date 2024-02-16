from setuptools import setup, find_packages

setup(
    name="HVAE",
    version="0.1",
    description="Hierarchical Variational Autoencoder",
    author="Sebasitan Meznar",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "torch",
        "rustimport",
        "editdistance",
        "scikit-learn",
        "tqdm",
        "commentjson",
        "pymoo",
    ],
)
