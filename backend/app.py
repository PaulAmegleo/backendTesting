import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import nltk
import spacy
from nltk.corpus import stopwords
import string
import difflib

app = Flask(__name__)
CORS(app)

# Download necessary NLTK data files

# Download spaCy model if not already downloaded
try:
    spacy.load("en_core_web_sm")
except OSError:
   
    spacy.load("en_core_web_sm")

nlp = spacy.load("en_core_web_sm")

def search(query, search_type='title'):
    if search_type == 'author':
        url = f'https://openlibrary.org/search/authors.json?q={query}'
    else:
        url = f'https://openlibrary.org/search.json?q={query}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

def parse_author_search_results(json_data):
    authors = [
        {
            'name': doc.get('name', 'N/A'),
            'key': doc.get('key', '')
        }
        for doc in json_data.get('docs', [])
    ]
    
    # Use spaCy and string similarity to disambiguate authors
    unique_authors = {}
    for author in authors:
        name = author['name']
        doc = nlp(name)
        # Check for entities in the text
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                if ent.text not in unique_authors:
                    unique_authors[ent.text] = author['key']
                else:
                    # Use string similarity to check for near duplicates
                    similarity = difflib.SequenceMatcher(None, ent.text, name).ratio()
                    if similarity < 0.85:
                        unique_authors[ent.text] = author['key']
                break
    return [{'name': name, 'key': key} for name, key in unique_authors.items()]

def parse_book_search_results(json_data):
    return [
        {
            'title': doc.get('title', 'N/A'),
            'author': ', '.join(doc.get('author_name', ['N/A'])),
            'first_publish_year': doc.get('first_publish_year', 'N/A'),
            'key': doc.get('key', '')
        }
        for doc in json_data.get('docs', [])
    ]

def get_book_details(key):
    url = f'https://openlibrary.org/works/{key}.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        book_data = response.json()

        # Extract genres from subjects
        genres = book_data.get('subjects', [])

        # Process genres with NLP to get top 3
        top_genres = extract_top_genres(genres)

        # Add top genres to book data
        book_data['genres'] = top_genres

        return book_data
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

def extract_top_genres(genres):
    # Process the genres to remove duplicates and clean the data
    processed_genres = [preprocess_text(genre) for genre in genres]
    
    # Use spaCy to get the most relevant genres
    doc = nlp(' '.join(processed_genres))
    genre_freq = {}
    
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN']:
            genre_freq[token.text] = genre_freq.get(token.text, 0) + 1
    
    # Sort genres by frequency and get the top 3
    sorted_genres = sorted(genre_freq.items(), key=lambda x: x[1], reverse=True)
    top_genres = [genre for genre, _ in sorted_genres[:3]]

    return top_genres



def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return ' '.join(word for word in text.split() if word not in stop_words)

def recommend_books(base_book, books):
    descriptions = []
    book_keys = []

    for book in books:
        book_key = book['key'].replace('/works/', '')
        details = get_book_details(book_key)
        if details:
            description = details.get('description', '')
            if isinstance(description, dict):
                description = description.get('value', '')
            descriptions.append(preprocess_text(description))
            book_keys.append(book['key'])

    if not descriptions:
        print("No descriptions available for recommendations.")
        return []

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(descriptions)

    base_book_index = book_keys.index(base_book['key'])
    cosine_similarities = linear_kernel(tfidf_matrix[base_book_index:base_book_index + 1], tfidf_matrix).flatten()

    related_docs_indices = cosine_similarities.argsort()[:-6:-1]
    return [books[i] for i in related_docs_indices if i != base_book_index]


def get_author_works(author_key):
    url = f'https://openlibrary.org/authors/{author_key}/works.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None
    
def get_author_details(author_key):
    url = f'https://openlibrary.org/authors/{author_key}.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

@app.route('/api/authors/<author_key>', methods=['GET'])
def api_author_details(author_key):
    author_details = get_author_details(author_key)
    if author_details:
        return jsonify(author_details)
    else:
        return jsonify({'error': 'Author details not found'}), 404

@app.route('/api/author/<author_key>/works', methods=['GET'])
def api_author_works(author_key):
    works_data = get_author_works(author_key)
    if works_data and 'entries' in works_data:
        works = [{'title': work.get('title', 'N/A'), 'key': work.get('key', '')} for work in works_data['entries']]
        return jsonify(works)
    else:
        return jsonify({'error': 'Works not found'}), 404

@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'title')
    results = search(query, search_type)
    if search_type == 'author':
        parsed_results = parse_author_search_results(results)
    else:
        parsed_results = parse_book_search_results(results)
    return jsonify(parsed_results)

@app.route('/api/book/works/<key>', methods=['GET'])
def api_book_details_with_recommendations(key):
    details = get_book_details(key)
    if not details:
        return jsonify({'error': 'Book details not found'}), 404

    # Fetch search results to use for recommendations
    search_results = search(details['title'])
    books = parse_book_search_results(search_results)

    # Generate recommendations
    recommendations = recommend_books(details, books)

    # Add recommendations to the details response
    details['recommendations'] = recommendations

    return jsonify(details)



if __name__ == "__main__":
    app.run(debug=True)
