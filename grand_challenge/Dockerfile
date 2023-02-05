FROM python:3.9-slim

RUN apt update
RUN apt install -y git

RUN groupadd -r evaluator && useradd -m --no-log-init -r -g evaluator evaluator

RUN mkdir -p /opt/evaluation /opt/evaluation/ground-truth /input /output \
    && chown -R evaluator:evaluator /opt/evaluation /input /output

USER evaluator
WORKDIR /opt/evaluation

ENV PATH="/home/evaluator/.local/bin:${PATH}"

RUN python -m pip install --user -U pip

ARG GT_SEGMENTATION_PATH
COPY --chown=evaluator:evaluator ${GT_SEGMENTATION_PATH} /opt/evaluation/ground-truth
ARG JSON_CONFIG_PATH
COPY --chown=evaluator:evaluator ${JSON_CONFIG_PATH} /opt/evaluation/ground-truth/config.json

COPY --chown=evaluator:evaluator ./challenge_eval/requirements.txt /opt/evaluation/
RUN python -m pip install --user -rrequirements.txt


COPY --chown=evaluator:evaluator ./challenge_eval/*.py /opt/evaluation/

# https://stackoverflow.com/questions/34324277/how-to-pass-arg-value-to-entrypoint
# ENV _GT_SEGMENTATION_PATH=${GT_SEGMENTATION_PATH}

ENTRYPOINT python evaluation.py --input /input --data ground-truth --output /output --config ground-truth/config.json --optimize && mv /output/*metrics.json /output/metrics.json
