from distribute import setup, find_packages

setup(
    name = "SAPIENTA",
    version = 0.1,
    packages = find_packages(),

    #install requirements
    install_requires = ['Flask>0.9',
        'text-sentence>=0.14'],

    author="James Ravenscroft",
    author_email = "ravenscroft@papro.org.uk",
    description = "Toolkit for annotating XML scientific papers with CoreSC labels",
    url="http://www.sapientaproject.com/"
        
)
