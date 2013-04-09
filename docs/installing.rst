Installing
----------
Installing RNDR is easy and can be done in three ways: 
    * installing from PyPI using a package manager.
    * downloading the archive file directly from the PyPI downloads page.
    * installing the developmental version directly from the source code repository.

Using A Package Manager
~~~~~~~~~~~~~~~~~~~~~~~
    1. Pass the necessary parameters and the rndr name to a package manager
           like `pip`_ or `easy_install`_::

            pip install  rndr
            easy_install rndr
            
       
.. _pip: http://pypi.python.org/pypi/pip
.. _easy_install: http://pypi.python.org/pypi/setuptools

Using The Archive File
~~~~~~~~~~~~~~~~~~~~~~
    1. Obtain the tar file from the download section of the `PyPI page`_.
    2. Unzip the archive and run installation script.::

           tar vxf RNDR-<version>.tar.gz
           cd RNDR-<version>
           sudo python setup.py install

.. _PyPI page: http://pypi.python.org/pypi/rndr/

From the Source
~~~~~~~~~~~~~~~
    1. Download the latest stable version of RNDR from its `Github repository`_.::

           git clone https://github.com/alem/rndr rndr

    2. Run the installation script.::

           cd rndr/rndr/
           sudo python setup.py install

.. _Github repository: https://github.com/alem/rndr
