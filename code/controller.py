# this file controls the workflow of downloading files from the API, renaming and converting them, and computing metrics for them

CSV = './data/results.csv'

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='control the pipeline')
    parser.add_argument('-t', type=str, help='TEASE')
    parser.add_argument('-a', type=str, help='toke')
    return parser.parse_args()


def api(tease, toke):
    from func.jatosppi import get_data, get_met, convert_beh, move_txt, push
    import os


    text_files = get_data(get_met(tease), tease)
    all_paths = convert_beh(text_files)
    move_txt(text_files)
    #push(toke)
    print('done with api ', all_paths)
    return all_paths



def compute(submission, scores, toke):
    from func.comput_metrics import compute
    from func.jatosppi import push

    new_scores = compute(submission, scores)
    
    # Ensure unique subject name
    if 'sub_name' not in new_scores.columns or new_scores['sub_name'].isnull().any():
        new_scores['sub_name'] = submission.get('sub_name', f"Participant_{len(scores) + 1}")
    
    print("New scores:\n", new_scores)

    # Append new scores to the existing DataFrame
    scores = pd.concat([scores, new_scores], ignore_index=True)
    
    return scores

def create_html_object(scores):
    users = []
    print("Scores DataFrame:\n", scores)
    
    for _, row in scores.iterrows():
        try:
            user = {
                "number": str(row['rank']),
                "name": row['sub_name'],
                "points": str(row['composite'])
            }
            print(f"Adding user: {user}")  # Debugging statement
            users.append(user)
        except KeyError as e:
            print(f"KeyError: {e} is missing in scores DataFrame.")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    print("Final users list:", users)
    return users

def create_html(users):
    from func.update_html import update_html, generate_rows

    update_html('./index.html', users)


    return None





if __name__ == "__main__":
    import pandas as pd
    args = parse_args()
    submission = api(args.t, args.a)
    scores = pd.read_csv(CSV)
    print("Scores before compute step: ", scores)
    for sub in range(len(submission)):
        #merge scores df with the new scores
        scores = compute(submission[sub], scores, args.a)
        # After the loop
    scores.to_csv(CSV, index=False)
    print("Scores after compute step: ", scores)
    scores = pd.read_csv(CSV)
    print("Scores DataFrame after reading CSV:\n", scores)
    print("Scores columns:", scores.columns)
    users = create_html_object(scores)
    print("Users list before create_html:", users)
    print("Type of users:", type(users))
    print("Type of each entry in users:", [type(user) for user in users])
    create_html(users)
    print('done')
