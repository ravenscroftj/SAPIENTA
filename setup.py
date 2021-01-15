from setuptools import setup, find_packages

setup(
    name = "SAPIENTA",
    version = 0.1,
    packages = find_packages(),

    #install requirements
    install_requires = [],

    entry_points = {"console_scripts" : [
        'pdfxconv = sapienta.tools.pdfxconv:main',
        'sapientacli = sapienta.processing.cli:main',
        'sapientmaster = sapienta.processing:main',
        'sapientworker = sapienta.processing.worker:main',
        'sapientaweb   = sapienta:main'
        ]},

    data_files = [('', ['ccg_binding.wsdl'])],
    include_package_data = True,
    author="James Ravenscroft",
    author_email = "ravenscroft@papro.org.uk",
    description = "Toolkit for annotating XML scientific papers with CoreSC labels",
    url="http://www.sapientaproject.com/"
        
)
