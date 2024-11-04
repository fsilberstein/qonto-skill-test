FROM apache/beam_python3.12_sdk:2.60.0

ARG PKG_SDIST
ENV BEAM_VERSION=2.60.0
ENV REPO_BASE_URL=https://repo1.maven.org/maven2/org/apache/beam

RUN apt-get update && apt-get install -y default-jdk

RUN mkdir -p /opt/apache/beam/jars \
  && wget ${REPO_BASE_URL}/beam-sdks-java-io-expansion-service/${BEAM_VERSION}/beam-sdks-java-io-expansion-service-${BEAM_VERSION}.jar \
          --progress=bar:force:noscroll -O /opt/apache/beam/jars/beam-sdks-java-io-expansion-service.jar

# Copy the pipeline code
COPY main.py requirements.txt dist/${PKG_SDIST} ./

# Install dependencies to launch the pipeline
RUN pip install -r requirements.txt && pip install ${PKG_SDIST}
