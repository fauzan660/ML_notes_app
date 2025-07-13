import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from cleantext import clean

def remove_stopwords(sent, language):
    stop_words = set(stopwords.words(language))
    word_tokens = sent.split()
    filtered_sent = [word for word in word_tokens if word not in stop_words]
    return filtered_sent

def remove_urls(sent):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', sent)

def remove_punctuation(sent):
    punctuation_pattern = r'[^\w\s]'
    sent = re.sub(punctuation_pattern, '', sent)
    return sent

def lowercase(sent):
    return sent.lower()

def remove_num_symbols(sent):
    text = re.sub(r'\d+', '', sent)  # remove numbers
    text = re.sub(r'\*+|#+|-+', ' ', text)  # remove markdown symbols
    return text
    
def remove_html(sent):
    html_tags_pattern = r'<.*?>'
    text_without_html_tags = re.sub(html_tags_pattern, '', sent)
    return text_without_html_tags

def remove_duplicates(sent):
    return list(set(sent))


def preprocess_text(sent):
    
    text = lowercase(sent)
    text = remove_urls(text)
    text = remove_html(text)
    text = remove_punctuation(text)
    text = remove_num_symbols(text)
    text = remove_stopwords(text, "english")
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in text]
    text = remove_duplicates(tokens)

    

    return " ".join(tokens)
    