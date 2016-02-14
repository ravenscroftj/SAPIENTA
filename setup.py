from setuptools import setup, find_packages

setup(
    name = "SAPIENTA",
    version = 0.1,
    packages = find_packages(),

    #install requirements
    install_requires = ['Flask>=0.9',
            'pycurl>=7.19.0',
            'progressbar>=2.3',
            #'text-sentence>=0.14',
            'lxml>=3.4.4',
            'pyavl>=1.12',
            'suds>=0.4',
            'Flask-SocketIO>=1.2'],

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
