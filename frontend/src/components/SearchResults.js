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
        const response = await axios.get('http://127.0.0.1:5000/api/search', { params: { q: query, type: type } });
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
              <Link to={`/book${result.key}`}>
                {result.title}
                {result.image && (
                  <img
                    src={result.image}
                    alt={`${result.title} cover`}
                    style={{ width: '50px', height: '75px', marginLeft: '10px' }}
                    />)}
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
