import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import nltk
from nltk.corpus import stopwords
import string

import json
import re
import csv


# tobe_removed = ["How do they paint the water without the paint mixing with water?","Since 'moles' means small burrowing animals, and 'moles' means a unit of chemical measurement, and moles are blind, and blind people cannot do chemically accurate calculations, therefore moles cannot measure chemical substances.","Since 'oxymoron' is a common term, and 'oxy' relates to oxygen, and 'moron' means someone unintelligent, and the opposite of a moron is a genius, and if a word exists there is an antonym, therefore oxygeniuses is a rhetorical device for existence.", "What has more calories - 100lbs of bricks or 100lbs of feathers?", "How can a piston engine handle four strokes with ease, but when human tries one they have to sit down all the time?"]
# tobe_added = ["Today I found a family of five moles in my lawn... Is it possible to calculate the molarity?","If a wood saw is used to saw wood, then why can't I use a chainsaw to saw chains?","If Britain uses the metric system, why do they weigh their money in pounds?", "If humans can grow up to 8 feet, why have I never seen anyone with more than 2?","If I flip a coin 1,000,000 times, what are the odds of me wasting my time?"]
def format_sentence(sentence):

    if sentence.startswith("\'") and sentence.endswith("\'"):
        sentence = sentence[1:-1].strip()
    sentence = sentence.replace("’", "'").replace("`", "'")

    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", sentence)

def clean_value(value):
    """Remove surrounding double quotes if present and strip whitespace."""
    if value.startswith("\"\"") and value.endswith("\"\""):
        value = value[1:-1].strip()
    value = value.replace("’", "'").replace("`", "'")
    return value

def convert_inner_quotes(text):
    """Convert inner double quotes to single quotes, keeping outer quotes unchanged."""
    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", text)
sentences_list=[]
with open("ruozhiba_label_updated.csv", 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:                
        sentence = clean_value(row[1].strip())
        sentence = convert_inner_quotes(sentence)  # Apply the transformation
        sentences_list.append(sentence)

print(len(sentences_list))

# Ensure stopwords are available
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Function to preprocess text
def preprocess_text(sentences):
    words = []
    for sentence in sentences:
        sentence = sentence.lower().translate(str.maketrans('', '', string.punctuation))
        words.extend(sentence.split())
    words = [word for word in words if word not in stop_words]
    return words

from matplotlib.colors import ListedColormap
from wordcloud import WordCloud

# Define the same approximate palette
custom_colors = [
    "#8FBBD9",  # teal-blue (bar 1)
    "#9FA982",  # sage/green (bar 2)
    "#C2A18E",  # light brown (bar 3)
    "#AB99AF",  # muted purple (bar 4)
    "#95A4B0",  # bluish gray (bar 5)
    "#D4BDA3",  # beige (bar 6)
    "#9297A1",  # gray (bar 7)
]



# Create a custom ListedColormap
my_cmap = ListedColormap(custom_colors)



# Preprocess text and count word frequencies
words = preprocess_text(sentences_list)
word_freq = Counter(words)

# Generate word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white', colormap=my_cmap,  
                      max_words=100, contour_color='black', contour_width=1).generate_from_frequencies(word_freq)

# Display word cloud
plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig("wordcloud.pdf", format="pdf", bbox_inches="tight")
plt.show()
