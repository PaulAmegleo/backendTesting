import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import axios from 'axios';

function SearchResults() {
  const [results, setResults] = useState([]);
  const { search } = useLocation();
  const queryParams = new URLSearchParams(search);
  const query = queryParams.get('query');
  const type = queryParams.get('type');

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await axios.get('/search', { params: { query, type } });
        setResults(response.data || []);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchResults();
  }, [query, type]);

  return (
    <div>
      <h2>Search Results</h2>
      <ul>
        {results.map((result, index) => (
          <li key={index}>
            {type === 'title' ? (
              <Link to={`/book/${result.key}`}>
                {result.title}
                {result.cover_id && (
                  <img
                    src={`http://covers.openlibrary.org/b/id/${result.cover_id}-M.jpg`}
                    alt={`${result.title} cover`}
                  />
                )}
              </Link>
            ) : (
              <Link to={`/author/${result.key}`}>
                {result.name}
              </Link>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default SearchResults;
