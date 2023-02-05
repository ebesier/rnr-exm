#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

./build.sh

# for VOLUME_NAME in rnrexm_zebrafish rnrexm_mouse rnrexm_c_elegan; do
for VOLUME_NAME in rnrexm_c_elegan; do
    VOLUME_SUFFIX=$(dd if=/dev/urandom bs=32 count=1 | md5sum | cut --delimiter=' ' --fields=1)

    docker volume create rnrexm-output-$VOLUME_SUFFIX

    # Do not change any of the parameters to docker run, these are fixed
    docker run --rm \
        --memory="4g" \
        --memory-swap="4g" \
        --network="none" \
        --cap-drop="ALL" \
        --security-opt="no-new-privileges" \
        --shm-size="128m" \
        --pids-limit="256" \
        -v $SCRIPTPATH/test/:/input/ \
        -v rnrexm-output-$VOLUME_SUFFIX:/output/ \
        $VOLUME_NAME

    docker run --rm \
        -v rnrexm-output-$VOLUME_SUFFIX:/output/ \
        python:3.9-slim cat /output/metrics.json | python -m json.tool

    docker volume rm rnrexm-output-$VOLUME_SUFFIX
done
