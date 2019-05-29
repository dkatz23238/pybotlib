Introduction
=============

``pybotlib`` is a python library for developing Robotic Process Automation projects easily with python primarily on Linux.
It contains the code for a central object that will maintain the state and behavior of the RPA.
The focus of the project is to accelerate RPA development at scale using open source technology.
The package is split into two parts the pybotlib.VirtualAgent object that will control the overall behavior of your RPA as well as pybotlib.utils that contain many useful functions for RPA developmet purposes.
Check out the API Documentation for more details.
The project is centered around open technologies and the believe that the future of digital transformation across business is rooted in a shared knowledge economy.

``pybotlib``'s offical version is only supported on Linux systems however there is a version for Windows 10 that can be cloned and used in github.
The main branch of the pybotlib github repo is the Windows branch while the branch that is linked to PyPI is the ubuntu-client-37 branch.

To start using ``pybotlib`` on any linux machine you must make sure the machine can run GUI apps and has python 3.7+ installed.

We recommend to run light weight virtual desktops within docker containers and develop cloud native "destructible" RPA armies that can be summoned at mass scale.

To learn more about RPA development best practices in general refer to the following Medium article here: https://itnext.io/the-modern-enterprise-business-in-code-c6a5e0f4ed7e.

To install ``pybotlib`` you can install via pip or setup.py. We recommend to use pip for the latest stable version.

.. code-block:: bash

   pip install pybotlib

To install from source:

.. code-block:: bash

  git clone -b ubuntu-client-37 pybotlib && cd pybotlib
  python setup.py install

As mentioned above, we recomend to use lightweight docker containers to run your RPA's.
To spin up a fully functioning Ubuntu with GUI desktop run the following command, then access it via any VNC client or through the browser.
More details on this container image can be found here: https://github.com/fcwu/docker-ubuntu-vnc-desktop

.. code-block:: bash

    docker run -p 6080:80 -p 5900:5900 -v /dev/shm:/dev/shm dorowu/ubuntu-desktop-lxde-vnc