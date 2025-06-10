# syntax=docker/dockerfile:1

FROM continuumio/miniconda3 AS base

WORKDIR /app

# Copy necessary files
COPY env.yaml .
COPY main.py .
COPY .env .
COPY DatabricksJDBC42-2.6.34.1058_2/DatabricksJDBC42.jar .

# Create the Conda environment
RUN conda env create -f env.yaml
# Remove conflicting 'java' in Conda env if present
RUN rm -f /opt/conda/envs/myenv/bin/java && \
    ln -s /usr/lib/jvm/java-17-openjdk-amd64/bin/java /opt/conda/envs/myenv/bin/java


# Export the environment for reproducibility
RUN conda run -n myenv conda env export > exported_env.yaml

# --- Final image ---
FROM continuumio/miniconda3

WORKDIR /app

# Copy project files and environment export
COPY --from=base /app/main.py .
COPY --from=base /app/.env .
COPY --from=base /app/DatabricksJDBC42.jar .
COPY --from=base /app/exported_env.yaml .

# Recreate environment from exported YAML
RUN conda env create -f exported_env.yaml
RUN rm -f /opt/conda/envs/myenv/bin/java && \
    ln -s /usr/lib/jvm/java-17-openjdk-amd64/bin/java /opt/conda/envs/myenv/bin/java

# Install system Java
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk-headless && \
    apt-get clean

# Set environment variables
# Set Java system path
# Find system Java path dynamically
RUN JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java)))) && \
    echo "export JAVA_HOME=$JAVA_HOME" >> /etc/profile.d/java_home.sh && \
    echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> /etc/profile.d/java_home.sh && \
    mkdir -p /opt/conda/envs/myenv/etc/conda/activate.d && \
    echo "export JAVA_HOME=$JAVA_HOME" > /opt/conda/envs/myenv/etc/conda/activate.d/java.sh && \
    echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> /opt/conda/envs/myenv/etc/conda/activate.d/java.sh && \
    echo "export LD_LIBRARY_PATH=\$JAVA_HOME/lib/server:\$LD_LIBRARY_PATH" >> /opt/conda/envs/myenv/etc/conda/activate.d/java.sh

# Set at container runtime too
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:/opt/conda/envs/myenv/bin:$PATH
ENV LD_LIBRARY_PATH=$JAVA_HOME/lib/server:$LD_LIBRARY_PATH




# Command to run the app
CMD ["conda", "run", "--no-capture-output", "-n", "myenv", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
