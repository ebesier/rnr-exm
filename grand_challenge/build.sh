#!/usr/bin/env bash
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
REPOPATH="$(dirname "$SCRIPTPATH")"
cd "$REPOPATH"

# docker build -t rnrexm_zebrafish "$REPOPATH" --build-arg GT_SEGMENTATION_PATH= --build-arg JSON_CONFIG_PATH=./challenge_eval/evaluation_configs/zebrafish_VAL_evaluation_config.json
# docker build -t rnrexm_mouse "$REPOPATH" --build-arg GT_SEGMENTATION_PATH= --build-arg JSON_CONFIG_PATH=./challenge_eval/evaluation_configs/mouse_VAL_evaluation_config.json
docker build -t rnrexm_c_elegan -f ./grand_challenge/Dockerfile . --build-arg GT_SEGMENTATION_PATH=./datasets/c_elegan_pair4_segmentation.h5 --build-arg JSON_CONFIG_PATH=./challenge_eval/evaluation_configs/c_elegan_VAL_evaluation_config.json
