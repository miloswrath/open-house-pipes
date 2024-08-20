# run Quality Check against new sub data

import os
import sys
import pandas as pd

def parse_cmd_args():
    import argparse
    parser = argparse.ArgumentParser(description='QC for ATS')
    parser.add_argument('-s', type=str, help='Path to submission')
    parser.add_argument('-o', type=str, help='Path to output for QC plots and Logs')
    parser.add_argument('-sub', type=str, help='Subject ID')

    return parser.parse_args()

def df(submission):
    submission = pd.read_csv(submission)
    return submission

def qc(submission):
    # convert submission to DataFrame
    submission = df(submission)
     # check if submission is a DataFrame
    if not isinstance(submission, pd.DataFrame):
        raise ValueError('Submission is not a DataFrame. Could not run QC')
    # check if submission is empty
    if submission.empty:
        raise ValueError('Submission is empty')
        
    
def plots(submission, output, sub):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os

    #load csv
    df = pd.read_csv(submission)
    test = df[df['condition'] == 'test']
    block1 = test[test['block_c'] == 1]
    block2 = test[test['block_c'] == 2]
    count1 = 0
    for i in range(len(block1)):
        if block1['response'].iloc[i] != 'None':
            count1 += 1
        
    count2 = 0
    for i in range(len(block2)):
        if block2['response'].iloc[i] != 'None':
            count2 += 1

    total_responses = [[count1, len(block1)], [count2, len(block2)]]
    correct = [[block1['correct'].sum(), len(block1)], [block2['correct'].sum(), len(block2)]]
    fig, ax = plt.subplots()
    barWidth = 0.35
    r1 = np.arange(len(total_responses))
    r2 = [x + barWidth for x in r1]
    plt.bar(r1, [x[0] for x in total_responses], color='b', width=barWidth, edgecolor='grey', label='Total Responses')
    plt.bar(r2, [x[0] for x in correct], color='r', width=barWidth, edgecolor='grey', label='Correct Responses')
    plt.xlabel('Block')
    plt.ylabel('Number of Responses')
    plt.ylim(0, 25)
    plt.title('Total and Correct Responses by Block')
    plt.xticks([r + barWidth/2 for r in range(len(total_responses))], ['Block 1', 'Block 2'])
    # show percentage of correct responses on each bar
    for i in range(len(total_responses)):
        plt.text(r1[i], total_responses[i][0] + 0.5, str(round(correct[i][0]/total_responses[i][1] * 100, 2)) + '%', color='black', ha='center')
        plt.text(r2[i], correct[i][0] + 0.5, str(round(correct[i][0]/total_responses[i][1] * 100, 2)) + '%', color='black', ha='center')
    #show total number of trials for each block
    for i in range(len(total_responses)):
        plt.text(r1[i], total_responses[i][0] + 2, '# of trials = ' + str(total_responses[i][1]) + '\n' + '# of responses = ' + str(total_responses[i][0]), color='black', ha='left')
    #move legend to below the plot
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), shadow=True, ncol=2)
    plt.savefig(os.path.join(output, f'{sub}_ATS_responses.png'))  
    plt.close()
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='block_c', y='response_time', data=test, showfliers=False, color='white')
    sns.stripplot(x='block_c', y='response_time', data=test, alpha=0.5, jitter=True, hue='correct')
    plt.title('Response time by Block', fontsize=15, pad=20, color="black")
    plt.savefig(os.path.join(output, f'{sub}_ATS_rt.png'))
    plt.close()
            

def main():

    #parse command line arguments
    args = parse_cmd_args()
    submission = args.s
    output = args.o
    sub = args.sub

    # check if submission is a csv
    if not submission.endswith('.csv'):
        raise ValueError('Submission is not a csv')
    # check if submission exists
    if not os.path.exists(submission):
        raise ValueError('Submission does not exist')
    # run QC
    qc(submission)
    
    print(f'QC passed for {submission}, generating plots...')
    # generate plots
    plots(submission, output, sub)
    return submission
    
    
if __name__ == '__main__':
    main()



