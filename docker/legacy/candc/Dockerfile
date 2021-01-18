FROM base/archlinux:latest


######################## Prime operating system ####################################

#make sure pacman keys are up to date
RUN pacman-key --refresh-keys
RUN pacman -Sy --noconfirm libstdc++5 base-devel libunistring wget p7zip

######################## build gsoap ####################################

#build gsoap because the latest in the repo doesn't work
RUN wget -O  gsoap.tar.gz http://sourceforge.net/projects/gsoap2/files/gSOAP/gSOAP%202.7.9f%20stable/gsoap_2.7.9f.tar.gz/download &&\
    tar xf gsoap.tar.gz &&\
    cd gsoap-2.7 &&\
    export CXXFLAGS='-fpermissive' &&\
    ./configure &&\
    make &&\
    make install

############################## Build C&C Tools ##############################

ADD https://www.dropbox.com/s/uoyu3jlr11wb9jd/candc-1.00.tbz2?dl=1 /candc.tbz2

# extract C&C archive
RUN tar xf /candc.tbz2 && mv /candc-1.00 /candc

#add patch to the FS
ADD candc.patch /candc/candc.patch
RUN cd /candc && patch -p1 -i candc.patch

RUN cd /candc && mv Makefile.unix Makefile && make && make soap

############################# EXTRACT MODELS #########################################
ADD https://www.dropbox.com/s/njqn9k8p9ew90yl/models.tar.bz2?dl=1 /models.tar.bz2
ADD https://www.dropbox.com/s/hgqutxw8yv3u0g7/pos_bio-1.00.tbz2?dl=1 /pos_bio.tbz2
ADD https://www.dropbox.com/s/281lsbcxugwbtky/super_coresc.tar.7z?dl=1 /super_coresc.tar.7z


# extract models
RUN tar xvjf /models.tar.bz2 

#extract bio models and place into correct location
RUN tar xvjf /pos_bio.tbz2 && mv /pos_bio-1.00 /models/pos_bio-1.00

#extract super core sc models and place into correct location
RUN 7z x -so /super_coresc.tar.7z | tar xf - -C /models/ 

#add the markedup replacement file
ADD https://www.dropbox.com/s/3c0xqz1woaxpfhb/markedup_new?dl=1 /models/parser/cats/markedup_new


################################## RUN SERVER #######################################

ADD run_server.sh /candc/bin/run_server.sh

EXPOSE 9004

ENTRYPOINT cd /candc/bin && ./run_server.sh
