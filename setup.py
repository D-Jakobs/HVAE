from setuptools import setup, find_packages

setup(
    name="HVAE",
    version="0.1",
    url="https://github.com/D-Jakobs/HVAE/tree/AESR",
    description="Hierarchical Variational Autoencoder",
    author="Sebasitan Meznar",
    author_email="example@gmail.com",
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
