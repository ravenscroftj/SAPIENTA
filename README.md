# SAPIENTA

This repository is the home of the code behind the [SAPIENTA Project]().

To use SAPIENTA we recommend visiting our flagship instance https://sapienta.dcs.aber.ac.uk/ which is kindly hosted by [Aberystwyth University Deparment of Computer Science](https://www.aber.ac.uk/en/cs/). For simple use cases you should find the [Web UI](https://sapienta.dcs.aber.ac.uk/ui) sufficient.

## Local Installation For Large Batch Annotation.

For non-developers who are looking to enrich large batches of scientific papers and in cases where our [freely available server]() is unavailable or insufficient, we provide a [docker-compose](https://docs.docker.com/compose/) configuration.

[Full instructions for configuring SAPIENTA in docker are available here](docs/docker-compose.md).

## Local Installation for Developers and Tinkerers

If you plan to make changes to SAPIENTA's models or code then you will need to do a full installation of the system and the docker configuration is likely to be insufficient for your needs. 

[A guide to installing SAPIENTA ready for local development is available here](docs/full-install.md)

## Citing SAPIENTA

If you use our webservice or our software as part of an academic work then please cite the following paper:

```bibtex
@article{liakata2012automatic,
        title={Automatic recognition of conceptualization zones in scientific articles and two life science applications},
        author={Liakata, Maria and Saha, Shyamasree and Dobnik, Simon and Batchelor, Colin and Rebholz-Schuhmann, Dietrich},
        journal={Bioinformatics},
        volume={28},
        number={7},
        pages={991--1000},
        year={2012},
        publisher={Oxford University Press}
}       
```           
