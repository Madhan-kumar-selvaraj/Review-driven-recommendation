# -*- coding: utf-8 -*-
# @Time    : 21/10/22
# @Author  : Madhan Kumar S
# @Email   : madhan.ks@logically.co.uk

import nltk
import spacy
import os
import pandas as pd
import contractions

nltk.download("words")
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk.tokenize.treebank import TreebankWordDetokenizer

pd.options.mode.chained_assignment = None
pd.set_option('display.max_colwidth', None)
# python3 -m spacy download en_core_web_sm
spacy_lib = spacy.load("en_core_web_sm")

pd.set_option("display.max_columns", 10)

dataframe = pd.read_json(
    r"/home/logically/Madhan/Personal/Projects/review_analyzer_model/review_extractors/google_reviews_erode_hospital_nov_14.json",
    lines=True)
# print(dataframe.columns)
# print(dataframe.info())

df_dropped = dataframe.drop(
    ["user", "review_date", "images", "extraction_date", "review_availability", "address", "url", 'name'], axis=1)
df_filter = df_dropped.copy()
df_filter = df_filter[df_filter.review_text != ""]

df_filter["rating"] = df_dropped["rating"].str.replace(" out of 5,", "").str.replace("Rated ", "")
df_filter.rating = df_filter.rating.astype(float).astype(int)
df_filter["rating"].value_counts()
df_filter["bi_ratings"] = df_filter["rating"].apply(lambda x: "Positive" if x > 3.0 else "Negative")
df_filter.bi_ratings.value_counts()
df_filter = df_filter[df_filter.columns[[3, 1, 2, 0, 4]]]
df_filter["contractions_review"] = df_filter["review_text"].apply(lambda x: contractions.fix(x))

words = set(nltk.corpus.words.words())
df_filter["processed_review"] = df_filter["contractions_review"].apply(
    lambda x: " ".join(word.lower() for word in nltk.wordpunct_tokenize(x) if word.lower() in words))

stopword_data = {"ourselves", "hers", "between", "yourself", "but", "again", "there", "about", "once", "during", "out",
                 "very", "having", "with", "they", "own", "an", "be", "some", "for", "do", "its", "yours", "such",
                 "into", "of", "most", "itself", "other", "off", "is", "s", "am", "or", "who", "as", "from", "him",
                 "each", "the", "themselves", "until", "below", "are", "we", "these", "your", "his", "through", "don",
                 "nor", "me", "were", "her", "more", "himself", "this", "down", "should", "our", "their", "while",
                 "above", "both", "up", "to", "ours", "had", "she", "all", "no", "when", "at", "any", "before", "them",
                 "same", "and", "been", "have", "in", "will", "on", "does", "yourselves", "then", "that", "because",
                 "what", "over", "why", "so", "can", "did", "now", "under", "he", "you", "herself", "has", "just",
                 "where", "only", "myself", "which", "those", "i", "after", "few", "whom", "t", "being", "if", "theirs",
                 "my", "against", "a", "by", "doing", "it", "how", "further", "was", "here", "than"}
df_filter["processed_review"] = df_filter["processed_review"].apply(lambda x: [token.lemma_ for token in spacy_lib(x) if
                                                                               not token.is_punct and not token.like_num and not token.is_space and not str(
                                                                                   token) in stopword_data])
df_filter["processed_review"] = df_filter["processed_review"].apply(
    lambda x: [token.lower() for token in x if not len(token.strip()) < 2 and not len(token.strip()) > 15])
df_filter["processed_review"] = df_filter["processed_review"].apply(lambda x: TreebankWordDetokenizer().detokenize(x))
positive_words = {'absolutely', 'accepted', 'acclaimed', 'accomplished', 'accomplishment', 'admirable', 'amazing',
                  'authentic', 'abundant', 'abundance', 'achiever', 'affluent', 'astonishing', 'awesome', 'adorable',
                  'beaming', 'beauty', 'beautiful', 'believe', 'beloved', 'beneficial', 'bestfriend', 'blessed',
                  'bliss',
                  'brave', 'breathtaking', 'bright', 'brilliant', 'brilliance', 'bravo', 'calm', 'calming', 'capable',
                  'captivating', 'caring', 'celebrate', 'certain', 'champ', 'champion', 'charitable', 'charm',
                  'charming', 'comfortable', 'committed', 'compassion', 'compassionate', 'confident', 'congratulations',
                  'correct', 'courage', 'courageous', 'courteous', 'creative', 'creativity', 'credible', 'credibility',
                  'daring', 'darling', 'dazzling', 'dear', 'dearest', 'dedicated', 'delicious', 'delight', 'delightful',
                  'dependable', 'developed', 'devoted', 'devotion', 'dignified', 'diligent', 'discipline',
                  'distinguished', 'divine', 'dream', 'dreamy', 'driven', 'dynamite', 'dynamo', 'earnest', 'easy',
                  'ecstatic', 'education', 'effective', 'effortless', 'elegant', 'empathy', 'eminent', 'empower',
                  'empowerment', 'endearing', 'enduring', 'energy', 'enjoy', 'enjoyable', 'enormous', 'enthusiasm',
                  'epic', 'equality', 'especial', 'essential', 'esteem', 'eternal', 'euphoria', 'everlasting', 'excel',
                  'excellent', 'excellence', 'exceptional', 'exciting', 'excitement', 'exhilarating', 'experienced',
                  'expert', 'exquisite', 'extensive', 'extraordinary', 'extravagance', 'exuberant', 'fabulous', 'fair',
                  'faith', 'faithful', 'familiar', 'famous', 'fancy', 'fantastic', 'fascinating', 'favorite',
                  'fearless',
                  'fidelity', 'fierce', 'fit', 'first', 'flawless', 'forever', 'forgiveness', 'fortunate', 'fortune',
                  'free', 'freedom', 'fresh', 'friend', 'fulfilling', 'fun', 'funny', 'generous', 'genius', 'gentle',
                  'genuine', 'gift', 'gifted', 'giving', 'glam', 'glamour', 'glee', 'glorious', 'goal', 'goodwill',
                  'gorgeous', 'gourmet', 'grace', 'grateful', 'gratitude', 'great', 'good', 'great', 'greatness',
                  'growth', 'handsome', 'happy', 'happiness', 'hardworking', 'harmony', 'health', 'healthy', 'heart',
                  'heaven', 'hello', 'helpful', 'hero', 'hilarious', 'holy', 'home', 'honest', 'honor', 'hope',
                  'humble',
                  'huge', 'humane', 'humility', 'humor', 'idyllic', 'imaginative', 'immaculate', 'immense',
                  'impeccable',
                  'important', 'impressive', 'incomparable', 'incredible', 'indispensable', 'infinite', 'ingenuity',
                  'inspiration', 'inspirational', 'inspiring', 'integrity', 'intelligence', 'intrepid', 'irreplaceable',
                  'irresistible', 'jackpot', 'jewel', 'jolly', 'joy', 'joyful', 'joyous', 'jubilee', 'juicy', 'jumbo',
                  'just', 'justice', 'keen', 'key', 'kind', 'kindness', 'kindred', 'king', 'kiss', 'knightly',
                  'knockout', 'knowledge', 'knowledgeable', 'large', 'laugh', 'laughter', 'lavish', 'leader', 'legacy',
                  'legendary', 'leisure', 'liberty', 'life', 'longevity', 'love', 'loving', 'loyal', 'loyalty', 'luck',
                  'lucky', 'luxury', 'magic', 'magical', 'magnificent', 'majestic', 'major', 'marvelous', 'massive',
                  'meaning', 'meaningful', 'merry', 'mighty', 'miracle', 'moral', 'mother', 'motivated', 'natural',
                  'neat', 'needed', 'necessary', 'new', 'nice', 'noble', 'nourishing', 'nourishment', 'nurse',
                  'nurture',
                  'nutritious', 'open', 'openminded', 'opportunity', 'optimism', 'optimistic', 'optimum', 'opulence',
                  'opulent', 'organic', 'original', 'outstanding', 'overjoy', 'paradise', 'partner', 'passion',
                  'passionate', 'patience', 'patriotic', 'peace', 'peaceful', 'perfect', 'phenomenal', 'pioneer',
                  'plenty', 'playful', 'polite', 'positive', 'power', 'powerful', 'precious', 'premium', 'pretty',
                  'prime', 'principle', 'prize', 'prodigy', 'pride', 'productive', 'promise', 'prosperous', 'proud',
                  'pure', 'purpose', 'quality', 'qualified', 'queen', 'quiet', 'quick', 'relax', 'rad', 'radiant',
                  'rapture', 'rainbow', 'ready', 'real', 'reassuring', 'regal', 'rejoice', 'rejuvenate', 'relationship',
                  'relevant', 'reliable', 'resilient', 'respect', 'respectful', 'responsible', 'restorative',
                  'rewarding', 'rich', 'righteous', 'romance', 'romantic', 'safe', 'scholar', 'savior', 'scrumptious',
                  'secure', 'selfless', 'sensational', 'sensible', 'serenity', 'sexy', 'sharp', 'shine', 'significant',
                  'sincere', 'smile', 'smart', 'sophisticated', 'spark', 'sparkle', 'special', 'splendid', 'star',
                  'strong', 'stunning', 'success', 'super', 'superb', 'supportive', 'surprise', 'survivor', 'sweet',
                  'sympathy', 'talent', 'tasty', 'teacher', 'team', 'teamwork', 'tenaciuos', 'thankful', 'thorough',
                  'thoughtful', 'thrive', 'timeless', 'together', 'togetherness', 'treasure', 'triumph', 'true',
                  'trust',
                  'trustworthy', 'truth', 'ultimate', 'unbeatable', 'unbelievable', 'unconditional', 'understanding',
                  'unforgettable', 'unique', 'united', 'unstoppable', 'uplifting', 'useful', 'utmost', 'utopia',
                  'unwavering', 'vip', 'valiant', 'valor', 'value', 'victory', 'virtue', 'warm', 'wealth', 'welcome',
                  'whole', 'wholesome', 'willpower', 'winner', 'wisdom', 'wise', 'wonderful', 'worthy', 'wow', 'xanadu',
                  'xfactor', 'xoxo', 'yeah', 'yay', 'yes', 'young', 'youth', 'youthful', 'yummy', 'zeal', 'zen', 'zest'}


def positive_negative_word_finder(sentence, token, index):
    try:
        return f"{token} {sentence[index + 1]}"
    except:
        return ""


df_filter["positive_words"] = df_filter.loc[:, "processed_review"].apply(
    lambda x: [positive_negative_word_finder(TreebankWordTokenizer().tokenize(x), token, index) for index, token in
               enumerate(TreebankWordTokenizer().tokenize(x)) if token in positive_words])
negative_words = {'abrasive', 'apathetic', 'controlling', 'dishonest', 'impatient', 'anxious', 'betrayed',
                  'disappointed', 'embarrassed', 'jealous', 'abysmal', 'bad', 'callous', 'corrosive', 'damage',
                  'despicable', 'donot', 'enraged', 'fail', 'gawky', 'haggard', 'hurt', 'icky', 'insane', 'jealous',
                  'lose', 'malicious', 'naive', 'not', 'objectionable', 'pain', 'questionable', 'reject', 'rude', 'sad',
                  'sinister', 'stuck', 'tense', 'ugly', 'unsightly', 'vice', 'wary', 'yell', 'zero', 'adverse', 'banal',
                  'cannot', 'corrupt', 'damaging', 'detrimental', 'dreadful', 'eroding', 'faulty', 'ghastly', 'hard',
                  'hurtful', 'ignorant', 'insidious', 'junky', 'lousy', 'mean', 'nasty', 'noxious', 'odious', 'perturb',
                  'quirky', 'renege', 'ruthless', 'savage', 'slimy', 'stupid', 'terrible', 'undermine', 'untoward',
                  'vicious', 'weary', 'yucky', 'alarming', 'barbed', 'clumsy', 'dastardly', 'dirty', 'dreary', 'evil',
                  'fear', 'grave', 'ignore', 'injure', 'insipid', 'lumpy', 'menacing', 'naughty', 'none', 'offensive',
                  'pessimistic', 'quit', 'repellant', 'scare', 'smelly', 'substandard', 'terrifying', 'unfair',
                  'unwanted', 'vile', 'wicked', 'angry', 'belligerent', 'coarse', 'crazy', 'dead', 'disease', 'feeble',
                  'greed', 'harmful', 'ill', 'injurious', 'messy', 'negate', 'petty', 'reptilian', 'scary', 'sobbing',
                  'suspect', 'threatening', 'unfavorable', 'unwelcome', 'villainous', 'woeful', 'annoy', 'bemoan',
                  'cold', 'creepy', 'decaying', 'disgusting', 'fight', 'grim', 'hate', 'immature', 'misshapen',
                  'negative', 'nothing', 'oppressive', 'plain', 'repugnant', 'scream', 'sorry', 'suspicious', 'unhappy',
                  'unwholesome', 'vindictive', 'worthless', 'anxious', 'beneath', 'criminal', 'deformed', 'disheveled',
                  'filthy', 'grimace', 'hideous', 'imperfect', 'missing', 'never', 'neither', 'poisonous', 'repulsive',
                  'severe', 'spiteful', 'unhealthy', 'unwieldy', 'wound', 'apathy', 'boring', 'collapse', 'cruel',
                  'deny', 'dishonest', 'foul', 'gross', 'homely', 'impossible', 'misunderstood', 'no', 'nowhere',
                  'poor', 'revenge', 'shocking', 'sticky', 'unjust', 'unwise', 'appalling', 'broken', 'confused', 'cry',
                  'deplorable', 'dishonorable', 'frighten', 'grotesque', 'horrendous', 'inane', 'moan', 'nobody',
                  'prejudice', 'revolting', 'shoddy', 'stinky', 'unlucky', 'upset', 'atrocious', 'contrary', 'cutting',
                  'depressed', 'dismal', 'frightful', 'gruesome', 'horrible', 'inelegant', 'moldy', 'nondescript',
                  'rocky', 'sick', 'stormy', 'unpleasant', 'awful', 'contradictory', 'deprived', 'distress', 'guilty',
                  'hostile', 'infernal', 'monstrous', 'nonsense', 'rotten', 'sickening', 'stressful', 'unsatisfactory'}
df_filter["negative_words"] = df_filter.loc[:, "processed_review"].apply(
    lambda x: [positive_negative_word_finder(TreebankWordTokenizer().tokenize(x), token, index) for index, token in
               enumerate(TreebankWordTokenizer().tokenize(x)) if token in negative_words])

hospital_name_groupby = df_filter.groupby("input")
subplot_fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=("Postive review", "Negative review"), specs=[[{"type": "pie"}, {"type": "pie"}]])
for hospital_name, group_df in hospital_name_groupby:
    try:
        temp = group_df[group_df['positive_words'].str.len() != 0].copy()
        temp['positive_words'] = temp['positive_words'].apply(lambda x: ",".join(list(filter(None, x))))
        words_df = temp.groupby(level='rating')['positive_words'].apply(','.join).reset_index()
        temp = group_df[group_df['negative_words'].str.len() != 0]
        temp['negative_words'] = temp['negative_words'].apply(lambda x: ",".join(list(filter(None, x))))
        words_df["negative_words"] = temp.groupby('rating')['negative_words'].apply(','.join).reset_index()[
            "negative_words"]
        words_df1 = words_df.assign(negative_words=words_df.negative_words.str.split(","))
        words_df1 = words_df1.assign(positive_words=words_df1.positive_words.str.split(","))
        words_df1.set_index("rating", inplace=True)
        positive_df = pd.DataFrame(words_df1["positive_words"].dropna()).loc[:, "positive_words"].apply(
            lambda x: pd.Index(x).value_counts().nlargest(10))
        negative_df = pd.DataFrame(words_df1["negative_words"].dropna()).loc[:, "negative_words"].apply(
            lambda x: pd.Index(x).value_counts().nlargest(10))
        positive_df.fillna(0, inplace=True)
        negative_df.fillna(0, inplace=True)
        positive_df = positive_df.T
        negative_df = negative_df.T
        positive_df = positive_df.loc[:, positive_df.columns.isin([4, 5])]
        positive_df = pd.DataFrame(positive_df.sum(axis=1))
        positive_df.reset_index(inplace=True)
        positive_df.rename(columns={0: "value", "index": "reviews"}, inplace=True)
        positive_df = positive_df[positive_df["value"] > 5].sort_values(by='value', ascending=False)
        positive_df = positive_df[positive_df["reviews"] != ""]
        positive_df.reset_index(drop=True, inplace=True)
        negative_df = negative_df.loc[:, negative_df.columns.isin([1, 2, 3])]
        negative_df = pd.DataFrame(negative_df.sum(axis=1))
        negative_df.reset_index(inplace=True)
        negative_df.rename(columns={0: "value", "index": "reviews"}, inplace=True)
        negative_df = negative_df[negative_df["value"] > 5].sort_values(by='value', ascending=False)
        negative_df = negative_df[negative_df["reviews"] != ""]
        negative_df.reset_index(drop=True, inplace=True)
        if not positive_df.empty and positive_df.shape[0] > 3 and not negative_df.empty and negative_df.shape[0] > 0:
            print("\n", hospital_name, "\n")
            subplot_fig.add_trace(
                go.Pie(labels=positive_df.reviews, values=positive_df.value, textinfo='label+value+percent',
                       insidetextorientation='radial'), row=1, col=1)
            subplot_fig.add_trace(
                go.Pie(labels=negative_df.reviews, values=negative_df.value, textinfo='label+value+percent',
                       insidetextorientation='radial'), row=1, col=2)
            # subplot_fig.show()
            subplot_fig.write_image(f"{hospital_name}.png")
        elif not positive_df.empty and positive_df.shape[0] > 3:
            fig = go.Figure(
                data=[go.Pie(labels=positive_df.reviews, values=positive_df.value, textinfo='label+value+percent',
                             insidetextorientation='radial', title=f"{hospital_name} -> Positive reviews")])
            # fig.show()
            fig.write_image(f"{hospital_name}.png")
        elif not negative_df.empty and negative_df.shape[0] > 3:
            fig = go.Figure(
                data=[go.Pie(labels=negative_df.reviews, values=negative_df.value, textinfo='label+value+percent',
                             insidetextorientation='radial', title=f"{hospital_name} -> Negative reviews")])
            # fig.show()
            fig.write_image(f"{hospital_name}.png")
    except:
        pass

image_tag = ""
for index, _ in enumerate(os.listdir("/home/logically/Madhan/Personal/Projects/review_analyzer_model")):
    if str(_).endswith(".png"):
        if index == 0:
            image_tag = f'<h3>{_}</h3>' + '<div class="chart"> ' + f'<img src="{_}">' + '</div>'
        else:
            image_tag = image_tag + f'<h3>{_}</h3>' + '<div class="chart"> ' + f'<img src="{_}">' + '</div>'

heading = '<h1>Reviews for hospitals at erode</h1>'
subheading = ''
now = datetime.now()
current_time = now.strftime("%m/%d/%Y %H:%M:%S")
header = '<div class="top">' + heading + subheading + '</div>'
footer = '<div class="bottom"> <h3> This Report has been Generated on ' + current_time + '</h3> </div>'
content = '<center>' + image_tag + '</center></div>'
html = header + content + footer
print(html)
with open("report.html", "w+") as file:
    file.write(html)
