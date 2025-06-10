# syntax=docker/dockerfile:1

FROM continuumio/miniconda3 AS build

WORKDIR /app

# Copy environment file and source
COPY env.yaml .
COPY main.py .

# Create Conda environment
RUN conda env create -f env.yaml

# Ensure conda is initialized and accessible
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

# Optional: force reinstall numpy (as in your original)
RUN conda run -n myenv pip install numpy --force-reinstall

# Clean conda cache
RUN conda clean -a

FROM continuumio/miniconda3

WORKDIR /app

# Copy the whole environment from build
COPY --from=build /opt/conda /opt/conda
COPY main.py .

ENV PATH=/opt/conda/envs/myenv/bin:$PATH

CMD ["conda", "run", "--no-capture-output", "-n", "myenv", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
