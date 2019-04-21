from setuptools import setup

#str
long_desc = open("README.md", mode="r").read()
#list
install_reqs = [i.replace("\n", "") for i in open("requirements.txt").readlines()]


setup(
    name="pybotlib",
    version="0.1",
    description="Object oriented python RPA library",
    license="MIT",
    long_description=long_desc,
    author="David Katz",
    python_requires='>3.7',
    author_email="davidemmanuelkatz@gmail.com",
    url="https://github.com/dkatz23238/pybotlib",
    packages=["pybotlib", "pybotlib.exceptions", "pybotlib.utils"],
    install_requires=install_reqs,
    classifiers=['Operating System :: POSIX',]
)
