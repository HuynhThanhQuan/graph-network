FROM ubuntu:16.04

LABEL com.nvidia.volumes.needed="nvidia_driver"
RUN apt-get update && apt-get install -y --no-install-recommends \
         build-essential \
         git \
         curl \
         ca-certificates \
         libjpeg-dev \
         libpng-dev \
         libglu1 \
         ssh \
         nano \
         htop

ENV PYTHON_VERSION=3.6
RUN curl -o ~/miniconda.sh -O  https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh  && \
     chmod +x ~/miniconda.sh && \
     ~/miniconda.sh -b -p /opt/conda && \
     rm ~/miniconda.sh && \
     /opt/conda/bin/conda install conda-build && \
     /opt/conda/bin/conda create -y --name py$PYTHON_VERSION python=$PYTHON_VERSION numpy pyyaml scipy ipython mkl&& \
     /opt/conda/bin/conda clean -ya
ENV PATH opt/conda/bin:/opt/conda/envs/py$PYTHON_VERSION/bin:$PATH
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64

RUN conda install --name py$PYTHON_VERSION ffmpeg matplotlib opencv && /opt/conda/bin/conda clean -ya
RUN conda install --name py$PYTHON_VERSION lxml django nltk pandas tensorflow -c anaconda
RUN conda install --name py$PYTHON_VERSION natsort gensim psycopg2 -c conda-forge && /opt/conda/bin/conda clean -ya

RUN /opt/conda/envs/py$PYTHON_VERSION/bin/pip install easydict ffmpy imutils requests flask

RUN conda install --name py$PYTHON_VERSION --yes ipython notebook jupyter jupyterlab && conda clean -ya

EXPOSE 8888
EXPOSE 8008
EXPOSE 8080
EXPOSE 8081
EXPOSE 8082
EXPOSE 8083

WORKDIR /workspace
RUN chmod -R a+w /workspace

ENV JUPYTER_COMMAND "jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser --allow-root --NotebookApp.token="
CMD $JUPYTER_COMMAND
