import json
import os
import argparse



def main(args):
    _version=0.1
    output_dir=args.output_dir
    #evaluation_methods
    evals=[]

    if args.sdlogj:
        evals.append({"name": "LogJacDetStd",
                     "metric": "sdlogj"})

    if args.dice:
        evals.append({"name": "DSC",
                     "metric": "dice"})

    if args.hd95:
        evals.append({"name": "HD95",
                     "metric": "hd95"})


    if args.expected_shape is not None:
        expected_shape = args.expected_shape
    
    ##eval pairs
    with open(args.pairs_config, 'r') as f:
        json_data=json.load(f)
        task_name = json_data['name']
    if args.test:
        eval_pairs = json_data['registration_test']
        teststring='_TEST_'
    else:
        eval_pairs = json_data['registration_validation']
        teststring='_VAL_'


    #write config
    evaluation_config={ 
                        'task_name':task_name,
                        'eval_config_version':_version,
                        'evaluation_methods': evals,
                        'expected_shape':expected_shape,
                        'eval_pairs':eval_pairs,

                        }

    with open(os.path.join(output_dir,task_name+teststring+'evaluation_config.json'), 'w') as f:
        json.dump(evaluation_config,f, indent=4)

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Create task_dataset_config.json for RnR-ExM challenge dataset")
    parser.add_argument("-s","--shape", dest='expected_shape', help="expected shape of deformation field", required=True, nargs='+',type=int, default=["a", "b","c","d"])
    parser.add_argument("-o","--output", dest="output_dir", help="path to write evaluation.json", required=False, default='.')
    parser.add_argument("-c","--config", dest="pairs_config", help="path to {TASKNAME}_dataset.json", required=True)
    parser.add_argument("--test", dest="test", action=argparse.BooleanOptionalAction, default=False) #Otherwise Validation
    parser.add_argument("--SDlogJ", dest="sdlogj", help="Evaluate SDlogJ", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--DSC", dest="dice", help="Evaluate dice", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--HD95", dest="hd95", help="Evaluate hd95", action=argparse.BooleanOptionalAction, default=False)

    args= parser.parse_args()
    main(args)