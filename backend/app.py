from flask import Flask, request, jsonify
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import nltk
import spacy
from nltk.corpus import stopwords
import string
import difflib

# Ensure necessary NLTK data files are downloaded
nltk.download('stopwords')

# Ensure spaCy model is downloaded
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

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
            'key': doc.get('key', ''),
            'cover_id': doc.get('cover_i', None)
        }
        for doc in json_data.get('docs', [])
    ]

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
        
        # Add static ratings
        book_details['ratings'] = 4.5
        
        return jsonify(book_details)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
