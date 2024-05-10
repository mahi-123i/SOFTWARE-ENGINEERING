import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,  accuracy_score
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import pickle


nltk.download('punkt')
nltk.download('stopwords')



data_path = 'bug.csv'  

data = pd.read_csv(data_path)


stop_words = set(stopwords.words('english'))

def clean_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    return ' '.join(filtered_tokens)

data['cleaned_summary'] = data['Summary'].apply(clean_text)




X_train, X_test, y_train, y_test = train_test_split(data['cleaned_summary'], data['Severity'], test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer()
X_train_1 = vectorizer.fit_transform(X_train)
X_test_1 = vectorizer.transform(X_test)


model = LogisticRegression()
model.fit(X_train_1, y_train)
predictions = model.predict(X_test_1)


report = classification_report(y_test, predictions)
print(report)



accuracy = accuracy_score(y_test, predictions)
print("Accuracy:", accuracy)

feature_names = vectorizer.get_feature_names_out()
for i, class_label in enumerate(model.classes_):
    top_features = np.argsort(model.coef_[i])[-10:]  
    print(f"Top features for class {class_label}:")
    print([feature_names[j] for j in top_features])

with open('your_model.pkl', 'wb') as file:
    pickle.dump(model, file)

with open('your_vectorizer.pkl', 'wb') as file:
    pickle.dump(vectorizer, file)
