import pandas as pd

mainDict = {'ES1': ['lights', 'light', 'furniture','furnitures', 'furniture\'s', 'clean', 'cleanliness', 'cleaned',
                   'cleanse', 'carpets', 'sanitaries', 'carpet', 'sanitary', 'secure', 'secured', 'sturdy',
                   'outdoor', 'curtains', 'blinds', 'dirty', 'dirt', 'mud', 'play area', 'park', 'safe', 'safety',
                   'safely', 'playground', 'ground', 'play', 'shade', 'smell', 'odor', 'space', 'classes', 'class',
                   'room', 'environment', 'bright', 'facility'],
            'ES2': ['greet', 'greets', 'greeted', 'greeting', 'warm', 'cozy', 'snug' 'smiles', 'smile', 'hugs', 'hug',
                   'allergies', 'allergy', 'meals', 'meal', 'food', 'nourishment', 'sustenance', 'nutriment', 'fare',
                   'bread', 'eat', 'consume', 'devour', 'ingest', 'snacks', 'snack', 'mat', 'bed', 'beds',
                   'crib', 'sleep', 'sleeping', 'nap', 'germs', 'germ', 'wash hands', 'first aid', 'toilet' 'washroom',
                   'nutrition', 'nutritious', 'rule', 'rules', 'hazard', 'hazards', 'hazardous', 'healthy'],
            'ES3': ['books', 'book', 'read', 'reading', 'reads', 'talk', 'talking', 'talks', 'communicate', 'communicate'
                   , 'communicate', 'interact', 'interactive', 'conversation', 'social', 'reading'],
            'ES4': ['blocks', 'block', 'crayons', 'crayon', 'puzzles', 'puzzle', 'storing', 'stored', 'storage',
                   'bins', 'bin', 'organized', 'organize', 'paper', 'papers', 'decorate', 'decorated', 'music', 'art',
                   'instruments', 'instrument', 'sing', 'singing', 'dance', 'dancing', 'acting', 'act', 'scissors',
                   'sand', 'bubbles', 'bubble', 'science', 'animals', 'animal', 'counting', 'count', 'puzzles', 'puzzle'
                   'science', 'nature', 'experiments', 'experiment', 'TV', 'computer', 'computers', 'laptop', 'shapes',
                   'counting', 'math', 'Sesame Street', 'toys', 'toy', 'activities', 'play', 'plays'],
            'ES5': ['supervise', 'supervisor', 'supervision', 'safety', 'safe', 'yell', 'belittle', 'scream', 'spank',
                   'shout', 'discipline', 'physical', 'punish', 'hurt', 'injure', 'wound', 'damage', 'abuse', 'disable',
                   'incapacitate', 'maim', 'mutilate', 'wrench', 'reward', 'conflict', ' behavior problem', 'teasing',
                   'bickering', 'fighting', 'bullying', 'name calling', 'rude', 'professional'],
            'ES6': ['price', 'cost', 'expensive', 'affordable', 'tuition', 'pay', 'due', 'money', 'charge', 'charges',
                   'fee', 'fees'],
            'ES7': ['convenient', 'convenience', 'accessible', 'hours', 'hour', 'location', 'time', 'day', 'days',
                   'open', 'long', 'short', 'summer', 'daily', 'picked', 'front', 'parking', 'parking lot', 'close',
                   'location', 'easy', 'far', 'early', 'open', 'hours', 'hours', 'work'],
            'ES8': ['ratio', 'ratios', 'regulation', 'regulations', 'inspection', 'inspections', 'violation',
                   'violations' 'credentials', 'credential', 'early childhood education', 'ECE', 'elementary education',
                   'certified teacher', 'background check', 'first aid', 'fingerprint', 'criminal background'],
            'ES9': ['religion', 'religious', 'Christian', 'Jewish', 'Catholic'],
            'D10': ['curriculum', 'learning,', 'learn', 'learned', 'teach', 'taught', 'development', 'preschool',
                    'skills', 'education', 'Montessori'],
            'D11': ['recommend', 'recommends', 'recommendation', 'recommended', 'highly', 'refer', 'refers', 'referral',
                    'referrals', 'decision', 'sending', 'decided', 'review', 'reviews', 'stars'],
            'D12': ['tour', 'toured', 'visit', 'visited', 'questions', 'schedule', 'phone', 'talk', 'talks', 'talked',
                    'look', 'looks', 'looked', 'initial']
            }
def join_data(LIWC, DT, final):
    df2 = pd.read_csv(DT, low_memory=False)
    mylist = list()
    for chunk in pd.read_csv(LIWC, chunksize=20000):
        mylist.append(chunk)
    df1 = pd.concat(mylist, axis=0)
    del mylist

    df = df1.merge(df2, left_on='count', right_on='id', how='outer')
    df.drop('text', axis=1, inplace=True)
    # df.drop('id', axis=1, inplace=True)
    df.rename(index=str, columns={"sentiment1": "DT_Sentiment", "polarity": "DT_Polarity"}, inplace=True)
    df.to_csv(final, index=False)
    pass


def generate_dimensions():
    mylist = list()
    for chunk in pd.read_csv('final_by_review.csv', chunksize=20000):
        mylist.append(chunk)
    df1 = pd.concat(mylist, axis=0)
    for dim, val in mainDict.iteritems():
        first = True
        for v in val:
            if first:
                df = df1[df1['review'].str.lower().str.contains(v.lower(), na=False)]
                first = False
            else:
                tempdf = df1[df1['review'].str.lower().str.contains(v.lower(), na=False)]
                df = pd.concat([df, tempdf])
        # df.drop_duplicates(subset='review_id', keep="last", inplace=True)
        df.to_csv('review_' + str(dim) + '.csv')


def generate_row_dimensions():

    global df
    for dim, val in mainDict.iteritems():
        first = True
        for chunk in pd.read_csv('final_by_row.csv', chunksize=20000):
            mylist = list()
            mylist.append(chunk)
            df1 = pd.concat(mylist, axis=0)
            for v in val:
                if first:
                    df = df1[df1['text'].str.lower().str.contains(v.lower(), na=False)]
                    first = False
                else:
                    tempdf = df1[df1['text'].str.lower().str.contains(v.lower(), na=False)]
                    df = pd.concat([df, tempdf])
        # df.drop_duplicates(subset='count', keep="last", inplace=True)
        df.to_csv('row_' + str(dim) + '.csv')


def data_by_row():
    df = pd.read_csv('review_master.csv')
    list_by_row = list()
    count = 1
    for index, row in df.iterrows():
        if pd.isnull(row['review']):
            continue
        text = row['review'].strip().replace('\n', '').replace('\r', '').replace('\t', '').replace('*', '')\
            .replace('(', '').replace(')', '').replace('"', '').split('.')
        for val in text:
            if val.strip() == '':
                continue
            list_by_row.append([count, row['review_id'], val.strip()])
            count += 1
    df1 = pd.DataFrame(list_by_row, columns=["id", "yelp_review_id", "text"])
    df1.to_csv('review_by_row.csv', index=False)

generate_row_dimensions()