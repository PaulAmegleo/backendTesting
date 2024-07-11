from flask import Flask, request, jsonify
import requests
import nltk
import spacy
from nltk.corpus import stopwords
import string
from collections import Counter
from flask_cors import CORS
from spacy.tokens import Doc

app = Flask(__name__)
CORS(app)  # Initialize CORS after creating the Flask app

# Ensure necessary NLTK data files are downloaded
nltk.download('stopwords')

# Ensure spaCy model is downloaded
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

# Extend spaCy with custom functions to handle text preprocessing
@spacy.Language.factory("custom_preprocessing")
def create_custom_preprocessing(nlp, name):
    return CustomPreprocessing()

class CustomPreprocessing:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def __call__(self, doc):
        return Doc(doc.vocab, [token for token in doc if token.text.lower() not in self.stop_words and token.text.lower() not in string.punctuation])

nlp.add_pipe("custom_preprocessing")

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
                    similarity = ent.similarity(nlp(unique_authors[ent.text]))
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
            'key': doc.get('key', ''),
            'cover_id': doc.get('cover_i', None),
            'language': doc.get('language', [])
        }
        for doc in json_data.get('docs', [])
        if 'eng' in doc.get('language', [])
    ]

def get_book_details(key):
    url = f'https://openlibrary.org{key}.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        book_details = response.json()
        
        # Add cover image URL
        cover_id = book_details.get('covers', [None])[0]
        if cover_id:
            book_details['cover_image'] = f'http://covers.openlibrary.org/b/id/{cover_id}-L.jpg'
        
        # Add static ratings for now
        book_details['ratings'] = 4.5
        
        # Clean subjects by merging similar terms
        subjects = book_details.get('subjects', [])
        cleaned_subjects = clean_subjects(subjects)
        book_details['subjects'] = cleaned_subjects

        # Fetch author details
        authors = book_details.get('authors', [])
        author_names = []
        for author in authors:
            author_key = author.get('author', {}).get('key', '')
            if author_key:
                author_url = f'https://openlibrary.org{author_key}.json'
                author_response = requests.get(author_url)
                author_response.raise_for_status()
                author_data = author_response.json()
                author_names.append(author_data.get('name', 'Unknown Author'))
        book_details['author_names'] = author_names

        # Check if the book is in English
        languages = book_details.get('languages', [])
        if not any(lang['key'].endswith('/eng') for lang in languages):
            return None

        return book_details
    except requests.exceptions.RequestException as e:
        return None

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return ' '.join(word for word in text.split() if word not in stop_words)

def clean_subjects(subjects):
    processed_subjects = [nlp(preprocess_text(genre)) for genre in subjects]
    unique_subjects = []
    grouped_subjects = []

    for genre in processed_subjects:
        matched = False
        for group in grouped_subjects:
            if any(genre.similarity(g) > 0.8 for g in group):
                group.append(genre)
                matched = True
                break
        if not matched:
            grouped_subjects.append([genre])

    # Sort groups by size (number of genres in each group) and take top 5
    grouped_subjects.sort(key=lambda x: len(x), reverse=True)
    top_genres = grouped_subjects[:5]

    # Extract genre names from the top groups
    unique_subjects = [max(group, key=lambda x: len(x.text)).text for group in top_genres]

    return unique_subjects

@app.route('/search', methods=['GET'])
def search_endpoint():
    query = request.args.get('query')
    search_type = request.args.get('type', 'title')
    search_result = search(query, search_type)
    
    if search_result:
        if search_type == 'author':
            authors = parse_author_search_results(search_result)
            return jsonify(authors)
        else:
            books = parse_book_search_results(search_result)
            return jsonify(books)
    else:
        return jsonify({"error": "No results found"}), 404

@app.route('/book/<key>', methods=['GET'])
def get_book_details_endpoint(key):
    book_details = get_book_details(f'/works/{key}')
    if book_details:
        return jsonify(book_details)
    else:
        return jsonify({"error": "No details found or book not in English"}), 404

@app.route('/highest_rated', methods=['GET'])
def get_highest_rated_books():
    # For simplicity, we'll use a static query that should return popular books.
    query = 'the'
    search_result = search(query)
    
    if search_result:
        books = parse_book_search_results(search_result)
        # Here we simply return the top 10 books. In a real-world scenario, you would likely have a more sophisticated rating system.
        highest_rated_books = sorted(books, key=lambda x: x.get('ratings', 0), reverse=True)[:10]
        return jsonify(highest_rated_books)
    else:
        return jsonify({"error": "No results found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
