import numpy as np
import scipy.stats
import pandas as pd
import os
import scipy
import argparse

np.set_printoptions(precision=3)

def task_ranking(RESULTS_PATH, TASK_NAME):

    def scores_better(task_metric):
        better = np.zeros((N,N))
        for i in range(N):
            for j in range(N):
                h,p = scipy.stats.ranksums(task_metric[i], task_metric[j])
                if((h>0)&(p<p_threshold)): #sign of h and p-value
                    better[i,j] = 1
        scores_task = better.sum(0)
        return scores_task

    def rankscore_avgtie(scores_int):
        N = len(scores_int)
        rankscale = np.linspace(.1,1,N) #our definition
        rankavg = np.zeros((N,2))
        scorerank = np.zeros(N)
        #argsort with reverse index
        idx_ = np.argsort(scores_int)
        idx = np.zeros(N).astype('int32')
        idx[idx_] = np.arange(N)
        #averaging ties
        for i in range(N):
            rankavg[scores_int[i],0] += rankscale[idx[i]]
            rankavg[scores_int[i],1] += 1
        rankavg = rankavg[:,0]/np.maximum(rankavg[:,1],1e-6)
        for i in range(N):
            scorerank[i] = rankavg[scores_int[i]]
        return scorerank

    def greaters(scores):
        return np.sum(scores.reshape(1,-1)>scores.reshape(-1,1),0)

    task = TASK_NAME
    base_path = RESULTS_PATH
    dim = np.load(os.path.join(base_path,'demo','{}_dice.npy'.format(task))).shape[0] # total num of labels in all the volumes of the task
    num_of_vol= np.load(os.path.join(base_path,'demo','{}_sdlogj.npy'.format(task))).shape[0] # num of volumes in the task
    p_threshold = 0.05

    unique_teams = os.listdir(base_path)

    #activate when 'Initial' baseline is available 

    # idx = unique_teams.index('Initial')
    # del unique_teams[idx]
    # unique_teams.insert(0,'Initial')


    # check if team submssion folder exist
    for team in reversed(unique_teams):
        if(os.path.isfile(base_path+team+'/{}_metrics.json'.format(task))):
            continue
        else:
            del unique_teams[unique_teams.index(team)]


    print("Number of teams {}".format(len(unique_teams)))
    N = len(unique_teams)

    dice_3 = np.zeros((N,dim))
    hd95_3 = 5*np.ones((N,dim))
    sdlogj_3 = 5*np.ones((N,num_of_vol))

    for ii,team in enumerate(unique_teams):

        if(os.path.isfile(os.path.join(base_path,unique_teams[ii],'/{}_dice.npy'.format(task)))):
            dice = np.load(os.path.join(base_path,unique_teams[ii],'/{}_dice.npy'.format(task)))
            dice[dice!=dice] = 0
            dice_3[ii] = dice
        if(os.path.isfile(os.path.join(base_path,unique_teams[ii],'/{}_hd95.npy'.format(task)))):
            hd95 = np.load(os.path.join(base_path,unique_teams[ii],'/{}_hd95.npy'.format(task)))
            hd95[hd95!=hd95] = 10
            hd95[hd95==np.Inf] = 10
            hd95_3[ii] = hd95
        if(os.path.isfile(os.path.join(base_path,unique_teams[ii],'/{}_sdlogj.npy'.format(task)))):
            sdlogj = np.load(os.path.join(base_path,unique_teams[ii],'/{}_sdlogj.npy'.format(task)))
            sdlogj_3[ii] = sdlogj

    #robustify
    dice0 = dice_3[0] #Initial baseline 
    dice3_30 = np.zeros((N,int(dice0.shape[0] * 0.3)))
    idx30 = np.argsort(dice0)[:int(dice0.shape[0] * 0.3)]
    for i in range(N):
        dice3_30[i] = dice_3[i,idx30]

    # Metric Ranking

    rank_all = np.zeros((N,4))
    scores = scores_better(dice_3)
    rank_dice3a = rankscore_avgtie(-scores.astype('int64'))
    rank_all[:,0] = rank_dice3a


    scores = scores_better(dice3_30)
    rank_dice3b = rankscore_avgtie(-scores.astype('int64'))
    rank_all[:,1] = rank_dice3b

    scores = scores_better(-hd95_3)
    rank_hd3 = rankscore_avgtie(-scores.astype('int64'))
    rank_all[:,2] = rank_hd3

    scores = scores_better(-sdlogj_3)
    rank_jac3 = rankscore_avgtie(-scores.astype('int64'))
    rank_all[:,3] = rank_jac3


    # Calculating arithmetic mean for each team

    dice_mean = dice_3.mean(1)
    sdlogj_mean = sdlogj_3.mean(1)
    hd95_mean = hd95_3.mean(1)
    dice_30_mean = dice3_30.mean(1)

    # Overall task ranking 

    ## rank geometric mean 
    all_rank_geo = np.power(np.prod(rank_all,axis=1),1/5)
    idx2 = np.argsort(-all_rank_geo)

    tasks_list = ["zebrafish", "mouse", "celegans"]
    task_id = tasks_list.index(task) + 1

    header = ['team', 'Dice_T{}'.format(task_id),'Dice30_T{}'.format(task_id),'HD95_T{}'.format(task_id),'sdLogJ_T{}'.format(task_id),'rank_T{}'.format(task_id)]
    df_rank = pd.DataFrame(columns=header)

    for i in range(N):
        team = unique_teams[idx2[i]]
        team_rank ={
            'team':team,
            'Dice_T{}'.format(task_id):dice_mean[idx2[i]],
            'Dice30_T{}'.format(task_id):dice_30_mean[idx2[i]],
            'HD95_T{}'.format(task_id):hd95_mean[idx2[i]],
            'sdLogJ_T{}'.format(task_id):sdlogj_mean[idx2[i]],
            'rank_T{}'.format(task_id):all_rank_geo[idx2[i]]
        }
        

        df_rank.loc[len(df_rank)] = team_rank

    df_rank.to_csv(os.path.join(base_path,'ranks','task_{}.csv'.format(task_id)))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description='RnR-ExM Ranking script')

    parser.add_argument("-i","--input", dest="results_path", help="path to results folder that has each team evaluation files", default="RnR-ExM",required=True)
    parser.add_argument("-t","--task", dest="task_name", help="Name of the task to evalaute", default="Zebrafish")
    args= parser.parse_args()

    task_ranking(args.results_path, args.task_name)