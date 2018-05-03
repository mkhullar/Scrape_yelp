import pandas as pd
import glob, math

baseDir = "C:/Users/mkhullar/PycharmProjects/ScrapeYelp/"


def merge_files():
    business_files = glob.glob('business*.csv')
    review_files = glob.glob('review*.csv')
    val = list()
    # for file in business_files:
    #     print(file)
    #     df = pd.read_csv(file, encoding='latin1')
    #     # if 'St._Louis' in file:
    #     #     val = [file.split('.json')[0].split('data_')[1].replace('_', '')] * len(df['yelp_id'])
    #     # else:
    #     #     val = [file.split('.')[0].split('data_')[1]] * len(df['yelp_id'])
    #     # df['City'] = val
    #     df.to_csv(file, index=False)
    # for file in review_files:
    #     print(file)
    #     df = pd.read_csv(file, encoding='latin1', engine='python')
    #     # val = [file.split('.')[0].split('data_')[1]] * len(df['yelp_id'])
    #     # df['City'] = val
    #     df.to_csv(file, index=False)
    df = pd.DataFrame()
    for file in business_files:
        print(file)
        df = df.append(pd.read_csv(baseDir+'CSV/'+file, encoding='latin1'))
    df.to_csv(baseDir+'Summary/'+'business_master.csv', index=False)
    df = pd.DataFrame()
    for file in review_files:
        print(file)
        df = df.append(pd.read_csv(baseDir + 'CSV/' + file, encoding='latin1', engine='python'))
    df.to_csv(baseDir + 'Summary/' + 'review_master.csv', index=False)


def get_by_row():
    df = pd.read_csv(baseDir + 'Summary/' + 'review_master.csv', encoding='latin1')
    wrap_list = []
    text = df['review']
    id = df['review_id']
    count = 1
    for index, val in enumerate(text):
        if pd.isnull(val):
            continue
        row_list = val.split('.')
        for row in row_list:
            if pd.isnull(row) or row.strip() == '':
                continue
            temp_list = list()
            temp_list.append(count)
            temp_list.append(row.strip().replace('\n', '').replace('\r', '').replace('\t', ''))
            temp_list.append(id[index] if id[index][0] != "=" else id[index][1:])
            count += 1
            wrap_list.append(temp_list)
    df = pd.DataFrame(wrap_list, columns=["id", "text", "yelp_review_id"])
    df.to_csv(baseDir + 'Summary/' + 'review_by_row.csv', index=False)

merge_files()
get_by_row()