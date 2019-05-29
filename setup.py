from setuptools import setup

#str
long_desc = """

For more info check out our documentation hosted on readthedocs: https://pybotlib.readthedocs.io

"""
#list
install_reqs = [
 'numpy',
 'selenium',
 'pandas',
 'requests',
 'lxml',
 'html5lib',
 'xlrd',
 'openpyxl',
 'mail-parser',
 'pygsheets',
 'minio',
 'BeautifulSoup4',
 'python3-xlib',
 'Xlib',
 'PyAutoGUI==0.9.39'
 ]




setup(
    name="pybotlib",
    version="0.1.5",
    description="Object oriented python RPA library",
    license="Apache 2.0",
    long_description=long_desc,
    author="David Katz",
    python_requires='>3.7',
    author_email="davidemmanuelkatz@gmail.com",
    url="https://github.com/dkatz23238/pybotlib/tree/ubuntu-client-37",
    packages=["pybotlib", "pybotlib.exceptions", "pybotlib.utils"],
    install_requires=install_reqs,
    classifiers=['Operating System :: POSIX',]
)
