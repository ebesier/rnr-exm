import json
import os.path
import pandas
import argparse
import numpy as np
import h5py

from utils import *
import os

def evaluate_ExM(INPUT_PATH,GT_PATH,JSON_PATH,OUTPUT_PATH,SAMPLING_FACTOR, verbose=False):
# def evaluate_ExM(INPUT_PATH,verbose=False):
    
    with open(JSON_PATH, 'r') as f:
        data = json.load(f)

    name=data['task_name']
    dataset = data['dataset']
    expected_shape=np.array(data['expected_shape'])
    evaluation_methods_metrics=[tmp['metric'] for tmp in data['evaluation_methods']]
    log_j = []
    missing_disp = []
    eval_pairs=data['eval_pairs']
    len_pairs=len(eval_pairs)

    #Check if all participants files are complete beforehand

    for idx, pair in enumerate(eval_pairs):
        # disp_name='disp_{}'.format(os.path.basename(pair))
        disp_name='{}_{}.h5'.format(name,dataset)
        disp_path=os.path.join(INPUT_PATH, disp_name)  
        with h5py.File(disp_path, "r") as f:
            pair_list = list(f.keys())
        if pair in pair_list:
            continue
        
        else:
            print("{},{} is missing".format(name,pair))
            missing_disp.append(pair)
            # raise_missing_file_error(disp_name) 

    #Dataframe for Case results

    cases_results=pandas.DataFrame()

    if verbose:
        print(f" Evaluate {len_pairs} cases : {[tmp['name'] for tmp in data['evaluation_methods']]}")

    for idx, pair in enumerate(eval_pairs):
        case_results={}

        volumes_pair_path=os.path.join(GT_PATH,"{}_{}_segmentation.h5".format(name,pair))
        with h5py.File(volumes_pair_path, "r") as f:
            fixed_seg = f['fixed'][()]
            moving_seg = f['move'][()]

        if os.path.basename(pair) in missing_disp:
            disp_field = np.zeros(expected_shape)
        else:
            disp_path=os.path.join(INPUT_PATH, '{}_{}.h5'.format(name,dataset))
            with h5py.File(disp_path, "r") as f:
                disp_field=f[pair][()]

            shape = np.array(disp_field.shape)
            if not np.all(shape==expected_shape):
                raise_shape_error(disp_name, shape, expected_shape)

        if SAMPLING_FACTOR != 1.0:
            fixed_seg = ndimage.zoom(fixed_seg, SAMPLING_FACTOR, order= 0)
            moving_seg = ndimage.zoom(moving_seg, SAMPLING_FACTOR, order= 0)
            disp_field = ndimage.zoom(disp_field, (SAMPLING_FACTOR,SAMPLING_FACTOR,SAMPLING_FACTOR,1), order= 1)

        D,H,W = fixed_seg.shape
        identity = np.meshgrid(np.arange(D), np.arange(H), np.arange(W), indexing='ij')
        warped_seg = map_coordinates(moving_seg, identity + disp_field.transpose(3,0,1,2), order=0)

        ## Get the volume labels 
        labels = list(np.unique(fixed_seg))
        labels.remove(0.0) # remove background

        ## iterate over designated evaluation metrics
        for _eval in data['evaluation_methods']:
            _name=_eval['name']

            ### SDlogJ
            if 'sdlogj' == _eval['metric']:
                jac_det = (jacobian_determinant(disp_field[np.newaxis, :, :, :, :].transpose((0,4,1,2,3))) + 3).clip(0.000000001, 1000000000)
                log_jac_det = np.log(jac_det)
                sd_log_j = log_jac_det.std()
                case_results[_name]= sd_log_j
                log_j.append(sd_log_j)


            ### DSC
            if 'dice' == _eval['metric']:
                dice = compute_dice(fixed_seg,moving_seg,warped_seg,labels)
                case_results[_name]=dice[0]
                if idx == 0:
                    dice_label = dice[1]
                else:
                    dice_label = np.concatenate((dice_label,dice[1]))

            ### HD95
            if 'hd95' == _eval['metric']:
                hd95 = compute_hd95(fixed_seg,moving_seg,warped_seg,labels)
                case_results[_name]=hd95[0]
                if idx == 0:
                    hd95_label = hd95[1]
                else:
                    hd95_label = np.concatenate((hd95_label,hd95[1]))


        if verbose:
            print(f'case_results [{idx}]: {case_results}')
        cases_results=pandas.concat([cases_results, pandas.DataFrame(case_results, index=[0])], ignore_index=True)
            
        
    aggregated_results = {}   
    for col in cases_results.columns:
        aggregated_results[col] = {'30': cases_results[col].quantile(.3),
                                'std': cases_results[col].std(),
                                'mean': cases_results[col].mean()}
    final_results={
        name: {
            "case": cases_results.to_dict(),
            "aggregates": aggregated_results
    }}

    missing_files = {
        "task":name,
        "missing_disp":missing_disp

    }

    #print(f'aggregated_results [{name}]: {aggregated_results}')
    if verbose:
        print(json.dumps(aggregated_results, indent=4))
    
    metrics_file_name = name + '_metrics.json' 
    with open(os.path.join(OUTPUT_PATH,metrics_file_name), 'w') as f:
        json.dump(final_results, f, indent=4)

    with open(os.path.join(OUTPUT_PATH,'{}_missing_deformation.json'.format(name)), 'w') as f:
        json.dump(missing_files, f, indent=4)

    np.save(os.path.join(OUTPUT_PATH,'{}_sdlogj.npy'.format(name)),np.array(log_j))
    np.save(os.path.join(OUTPUT_PATH,'{}_dice.npy'.format(name)),dice_label)
    np.save(os.path.join(OUTPUT_PATH,'{}_hd95.npy'.format(name)),hd95_label)



if __name__=="__main__":
    parser=argparse.ArgumentParser(description='RnR-ExM Evaluation script')

    parser.add_argument("-i","--input", dest="input_path", help="path to deformation fields", default="RnR-ExM",required=True)
    parser.add_argument("-d","--data", dest="gt_path", help="path to segmentation volumes", default="dataset")
    parser.add_argument("-o","--output", dest="output_path", help="path to write results(e.g. 'results/metrics.json')", default="metrics.json")
    parser.add_argument("-c","--config", dest="config_path", help="path to config json-File (e.g. '{ Task }_evaluation_config.json')", default='ground-truth/evaluation_config.json') 
    parser.add_argument("-s","--sampling_factor", dest="sampling_factor",help="downsample the segmentation map for faster evaluation",type=float, default=1)
    parser.add_argument("-v","--verbose", dest="verbose", action='store_true', default=True)
    args= parser.parse_args()

    evaluate_ExM(args.input_path, args.gt_path, args.config_path, args.output_path,args.sampling_factor, args.verbose)