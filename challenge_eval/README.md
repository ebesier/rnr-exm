# RnR-ExM Challenge Evaluation and Ranking

To evaluate the performance of the algorithms submitted to this challenge, we will use a variety of metrics that measure the accuracy and efficiency of the image registration process. Some common metrics include the Dice similarity coefficient, Hausdorff (HD95) metrics, robustness score and standard deviation of log Jacobian determinant of the deformation field. this folder includes:  

1. Create dataset configuration file `create_dataset_config.py`. 
2. Create evaluation and testing configuration file `create_evaluation_config.py`.
3. Evaluate the volumes alignment based on the participants' submitted deformation fields for the evaluation or testing dataset `evaluation.py`.
4. Ranking participants' score `ranking.py`. 

## Create dataset configuration file:

`create_dataset_config.py`

Create a JSON configuration file for each task's dataset, this configuration file is necessary to set the testing and evaluation pairs. 

- Dataset naming convention: 
```
Dataset
|_volumesTr
	|_{task_name}_Tr_pair_1.h5
	|_{task_name}_Tr_pair_2.h5
	..
|_volumesVal
	|_{task_name}_Val_pair_1.h5
	..
|_volumesTs
	|_{task_name}_Ts_pair_1.h5
```
- Args: *dataset_path* , *task_name* and *output_dir*.

- output : *{TASK_NAME}_dataset_config.json*.

- sample output:

```json
{
    "name": "zebrafish",
    "registration_test": [
        "volumesTs/zebrafish_Ts_pair_1.h5"
    ],
    "registration_validation": [
        "volumesVal/zebrafish_Val_pair_1.h5",
        "volumesVal/zebrafish_Val_pair_2.h5",
        "volumesVal/zebrafish_Val_pair_3.h5"
    ],
    "registration_training": [
        "volumesTr/zebrafish_Tr_pair_1.h5"
    ]
}
```

## Create evaluation configuration file:

`create_evaluation_config.py`

Create a JSON configuration file for each task's testing and evaluation dataset, the configuration file is necessary to run the alignment score in the next step. 

- Args:
    - --shape : expected deformation fields shape
    - --output : evaluation configuration file output directory. 
    - --config : path to the task dataset configuration file *{TASK_NAME}_dataset_config.json*.
    - --test : use test dataset else use evaluation dataset. 
    - --  : evaluate standard deviation of log Jacobian determinant of the deformation field.
    - --DSC : evaluate dice similarity coefficient.
    - --HD95: evaluate Hausdorff (HD95).

-  output: *{TASK_NAME}_VAL_evaluation_config.json* Or *{TASK_NAME}_TEST_evaluation_config.json* base on the `--test`. 

- sample output:

```json
{
    "task_name": "zebrafish",
    "eval_config_version": 0.1,
    "evaluation_methods": [
        {
            "name": "LogJacDetStd",
            "metric": "sdlogj"
        },
        {
            "name": "DSC",
            "metric": "dice"
        },
        {
            "name": "HD95",
            "metric": "hd95"
        }
    ],
    "expected_shape": [
        208,
        2048,
        2048,
        3
    ],
    "eval_pairs": [
        "volumesVal/zebrafish_Val_pair_1.h5",
        "volumesVal/zebrafish_Val_pair_2.h5",
        "volumesVal/zebrafish_Val_pair_3.h5"
    ]
}
```

## Evaluate the volumes alignment:

`evaluation.py`

Apply the alignment process on the selected pairs using the submitted deformation fields, then determine the alignment result score for each of the evaluation metrics (DSC, DSC30, HD95 & SDLOGJ)

- deformation fields name convention:
```
disp_{task_name}_Tr_pair_1.h5
disp_{task_name}_Val_pair_1.h5
```

- Args:
    - --input: path to the deformation fields directory
    - --data: path to dataset directory 
    - --output : directory path to store the evaluation outputs. 
    - --config : path to the evaluation configuration file, *{TASK_NAME}_VAL_evaluation_config.json* Or *{TASK_NAME}_TEST_evaluation_config.json*.
    - --sampling_factor: sampling factor to down/up sample the volumes and deformation fields.
    - --verbose: log progress. 

- down-sampling:
the current implementation down-sample the volumes and deformation fields base on `--sampling_factor` before the volumes alignment step.

- output:
    - `{Task_NAME}_metrics.json` : store the average score for each evaluation metrics and each volume. 
    - `{Task_NAME}_dice.npy`: store the DCS score for each label of each volume for team ranking. 
    - `{Task_NAME}_hd95.npy`: store the HD95 score for each label of each volume for team ranking.
    - `{Task_NAME}_sdlogj.npy`: store the SDLOGJ score for each label of each volume for team ranking.  


## Ranking participants' score

`ranking.py` 

THE ranking methods uses statistically significantly different results. For each metric applied in a task, methods are compared against each other (Wilcoxon signed rank test with p<0.05), ranked based on the number of ”won” comparisons and finally mapped to a numerical metric rank score between 0.1 and 1 (with possible score sharing). A task rank score is then obtained as the geometric mean of individual metric rank scores. 

- results directory tree:
```
evaluation results
    |__team_1
        |__{Task_NAME}_metrics.json
        |__{Task_NAME}_dice.json
        |__{Task_NAME}_hd95.json
        |__{Task_NAME}_sdlogj.json
    |__team_2
        |__{Task_NAME}_metrics.json
        |__{Task_NAME}_dice.json
        |__{Task_NAME}_hd95.json
        |__{Task_NAME}_sdlogj.json
    |__team_3
        |__{Task_NAME}_metrics.json
        ...
```



- Args:
    - --input: path to the results directory
    -  --task: task name to be ranked 

- Output: *task_{task number}.csv*.

- sample output:

|   | team  | Dice_T3            | Dice30_T3          | HD95_T3 | sdLogJ_T3              | rank_T3           |
|---|-------|--------------------|--------------------|---------|------------------------|-------------------|
| 0 | demo  | 0.997 | 0.997 | 0.0     | 3.748e-09 | 0.619 |
| 1 | demo2 | 0.997 | 0.997 | 0.0     | 3.748e-09 | 0.619 |
| 2 | demo3 | 0.997 | 0.997 | 0.0     | 3.748e-09 | 0.619 |
    