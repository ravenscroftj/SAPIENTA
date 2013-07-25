from setuptools import setup, find_packages

setup(
    name = "SAPIENTA",
    version = 0.1,
    packages = find_packages(),

    #install requirements
    install_requires = ['Flask>=0.9',
            'pycurl>=7.19.0',
            'progressbar>=2.3',
            'text-sentence>=0.14',
            'pyavl>=1.12'],

    entry_points = {"console_scripts" : [
        'pdfxconv = sapienta.tools.pdfxconv:main',
        'sapientmaster = sapienta.processing:main',
        'sapientworker = sapienta.processing.worker:main',
        'sapientaweb   = sapienta:main'
        ]},

    author="James Ravenscroft",
    author_email = "ravenscroft@papro.org.uk",
    description = "Toolkit for annotating XML scientific papers with CoreSC labels",
    url="http://www.sapientaproject.com/"
        
)
