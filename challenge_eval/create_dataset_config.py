import json
import os
import glob
import argparse


def main(args):

    dataset_path = args.dataset_path
    task_name = args.task_name

    registration_test = [os.path.relpath(x,dataset_path) for x in glob.glob(os.path.join(dataset_path,"volumesTs","{}_Ts*.h5".format(task_name)))]
    registration_validation = [os.path.relpath(x,dataset_path) for x in glob.glob(os.path.join(dataset_path,"volumesVal","{}_Val*.h5".format(task_name)))] 
    registration_training = [os.path.relpath(x,dataset_path) for x in glob.glob(os.path.join(dataset_path,"volumesTr","{}_Tr*.h5".format(task_name)))]


    #write config
    evaluation_config={ 
                        'name':task_name,
                        'registration_test':registration_test,
                        'registration_validation':registration_validation,
                        'registration_training':registration_training,
                        }

    with open(os.path.join(args.output_dir,'{}_dataset_config.json'.format(task_name)), 'w') as f:
        json.dump(evaluation_config,f, indent=4)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Create evaluation.json for RnR-ExM challenge")
    
    parser.add_argument("-d","--dataset_path", dest="dataset_path", help="path to the RnR-ExM dataset", required=False)
    parser.add_argument("-t","--task_name", dest="task_name", help="name of the task (zebrafish, mouse, celegans)", required=False,default="zebrafish") 
    parser.add_argument("-o","--output_dir", dest="output_dir", help="path to store the (task)_dataset_config.json", required=False)
       

    args= parser.parse_args()
    main(args)