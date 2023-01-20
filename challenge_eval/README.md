# RnR-ExM Challenge Evaluation

To evaluate the performance of the algorithms applied to align the challenge's different volumes, we will use a variety of metrics that measure the accuracy and efficiency of the image registration process. the metrics include the Dice similarity coefficient, Hausdorff (HD95) metrics, robustness score and standard deviation of log Jacobian determinant of the deformation field.

To evaluate your results before submitting the deformation fields to the RnR-ExM Challenge website, you can follow these steps:

1. create a python working environment and install the necessary library in the `requirements.txt`
2. in the same directory, we recommend you to create 3 new folders namely, `dataset`, `submission` and `results`.
3.  place the validation dataset segmentation `.h5` files inside `dataset` folder: 
```
dataset
    |__ c_elegan_pair4_segmentation.h5
    |__ mouse_pair4_segmentation.h5
    |__ zebrafish_pair4_segmentation.h5
```
4. Place your generated deformation fields `.h5` files in the `submission` folder. Please be aware of the naming convention for the deformation field to be {task_name}_val.h5 and the HDF5 dataset to be named `pair4` in the evaluation dataset case.

```
submission
    |__ c_elegan_val.h5
    |__ mouse_val.h5
    |__ zebrafish_val.h5
```


5. Run the evaluation script: to apply the alignment process on the selected pairs using the submitted deformation fields, then determine the alignment result score for each of the evaluation metrics (DSC, HD95 & SDLOGJ). The script takes a few arguments:   

- Args:
    - --input: path to the deformation fields directory `(submission/)`
    - --data: path to dataset directory `(dataset/)`
    - --output : directory path to store the evaluation outputs. `(results/)`
    - --config : path to the task evaluation configuration file *evaluation_configs/{TASK_NAME}_VAL_evaluation_config.json*.
    - --sampling_factor: sampling factor to down/up sample the volumes and deformation fields. *Could be used to speed up the evaluation process*
    - --verbose: log progress. 

Note: The `evaluation_configs` directory contains evaluation configuration files for each task, and based on which one is selected in the  `evlaution.py --config` that particular task will be evaluated.   

- Example to evaluate zebrafish alignment, Run:

```
python evlatiation.py \
--input /insert_working_directory/submission/ \
--data /insert_working_directory/dataset/ \
--output /insert_working_directory/results/ \
--config /insert_working_directory/evaluation_configs/zebrafish_VAL_evaluation_config.json \
--sampling_factor 0.5 
```

6. Once the evaluation done, you can check the output in the `results` directory, this file `{task_name}_metrics.json` would contain the score of each of our evaluation metrics. 

```json
"zebrafish": {
    "case": {
        "LogJacDetStd": {
            "0": 1.260214952323843e-07
        },
        "num_foldings": {
            "0": 0.0
        },
        "DSC": {
            "0": 1.5458373911564852e-06
        },
        "HD95": {
            "0": 247.4677326628076
        }
    }
}
```

## Notes
* Evaluation can take a long time and consume large memory depending on the size of the dataset. It is advisable to start from downsampled evaluation as shown above, with --sampling_factor 0.5 argument (1/2 downsampling). As an example, c_elegan_pair4 dataset having 580 Z-slices takes around ten minutes and uses 80 GB of RAM with a sampling factor of 0.5. Datasets with fewer Z-slices (mouse_pair4 and zebrafish_pair4) run faster (few minutes) with smaller RAM usage (10-20 GB). Without downsampling, the runtime and memory usage will be 8 times larger.

* Downsampled evaluation is a proxy for full-resolution evaluation.
  * DSC score will be similar with/without downsampling as it is an area ratio
  * HD95 will be roughly halved if evaluated with 1/2 downsampling as it is a distance-based metric
  * SDlogJ (indicated by LogJacDetStd in the output) tends to be larger when downsampled, although the relationship with the full-resolution counterpart is not trivial
  * num_foldings can be ignored (always 0)

* In the output json file, the "aggregates" entry shows the 30th percentile, mean, and standard deviation of all the "case" entries. In the validation phase, each animal species has one dataset, so these aggregate scores can be disregarded. They are the same as the "case" scores and the standard deviation is undefined (NaN).
