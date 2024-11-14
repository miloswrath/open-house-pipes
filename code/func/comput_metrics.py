import os
import sys
import pandas as pd
import numpy as np
import json

import pandas as pd
import pandas as pd

def compute(csv, scores):
    """
    This function takes in a CSV file and an existing scores DataFrame,
    computes new scores from the CSV, merges them with the existing scores,
    arranges them, and writes the final results back to the CSV.
    """
    # Step 1: Read the input CSV file
    df = pd.read_csv(csv)
    
    # Step 2: Filter and compute metrics
    test = df[df['condition'] == 'test']
    block1 = test[test['block_c'] == 1]
    block2 = test[test['block_c'] == 2]

    # Calculate the metrics for both blocks
    correct = [
        [block1['correct'].astype('int').sum(), len(block1)],
        [block2['correct'].astype('int').sum(), len(block2)]
    ]
    avg_time = [
        [block1['response_time'].mean(), len(block1)],
        [block2['response_time'].mean(), len(block2)]
    ]
    min_time = [
        [block1['response_time'].min(), len(block1)],
        [block2['response_time'].min(), len(block2)]
    ]
    max_time = [
        [block1['response_time'].max(), len(block1)],
        [block2['response_time'].max(), len(block2)]
    ]

    # Step 3: Calculate accuracy and composite score
    accuracy = [correct[0][0] / correct[0][1], correct[1][0] / correct[1][1]]
    composite = abs(1 / accuracy[0] - avg_time[0][0] * len(block1) - (max_time[0][0] - min_time[0][0])) + \
                abs(1 / accuracy[1] - avg_time[1][0] * len(block2) - (max_time[1][0] - min_time[1][0]))
    composite = int(round(composite / 2))

    # Get subject name
    sub_name = df['multichar_response'].iloc[0] if 'multichar_response' in df and not df.empty else 'unknown'
    
    # Step 4: Create a dictionary with the computed scores
    score_dict = {
        'sub_name': sub_name,
        'composite': composite,
        'rank': 0
    }

    # Step 5: Add the new score dictionary to the existing DataFrame
    scores = pd.concat([scores, pd.DataFrame([score_dict])], ignore_index=True)
    
    # Remove any rows where sub_name or composite is NaN
    scores = scores.dropna(subset=['sub_name', 'composite', 'rank'])

    # Step 6: Arrange scores by composite score and assign ranks
    scores = scores.drop_duplicates(subset=['sub_name'], keep='last')
    scores = scores.sort_values(by='composite', ascending=False).reset_index(drop=True)
    scores['rank'] = scores.index + 1

    # Step 7: Write the updated scores back to the CSV file
    #scores.to_csv(csv, index=False)

    print("Updated scores:")
    print(scores)

    return scores



