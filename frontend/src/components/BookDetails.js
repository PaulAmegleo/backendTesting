import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

function BookDetails() {
  const { key } = useParams();
  const [bookDetails, setBookDetails] = useState(null);
  const [authorName, setAuthorName] = useState(null);

  useEffect(() => {
    const fetchBookDetails = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/api/book/works/${key}`);
        const data = response.data;
        setBookDetails(data);

        // Extract author key from the first author in the list
        const authorKey = data?.authors?.[0]?.author?.key;
        if (authorKey) {
          // Fetch author details using the author key
          const authorResponse = await axios.get(`http://127.0.0.1:5000/api${authorKey}`);
          setAuthorName(authorResponse.data.name);
        }
      } catch (error) {
        console.error('Error fetching book details:', error);
      }
    };

    fetchBookDetails();
  }, [key]);

  const getDescription = (description) => {
    if (!description) return 'No description available';
    return typeof description === 'string' ? description : description.value;
  };

  return (
    <div>
      {bookDetails ? (
        <div>
          <h2>{bookDetails.title}</h2>
          {authorName ? (
            <p>
              Author: <a href={`https://openlibrary.org${bookDetails.authors[0].author.key}`} target="_blank" rel="noopener noreferrer">{authorName}</a>
            </p>
          ) : (
            <p>Loading author...</p>
          )}
          <p>First Published Year: {bookDetails.first_publish_year || 'Unknown'}</p>
          <p>Ratings: {bookDetails.rating ? bookDetails.rating.average.toFixed(1) : 'Not Rated'}</p>
          {bookDetails.covers && (
            <img
              src={`http://covers.openlibrary.org/b/id/${bookDetails.covers[0]}-M.jpg`}
              alt={`${bookDetails.title} cover`}
            />
          )}
          <p>Description: {getDescription(bookDetails.description)}</p>
          <p>Genres: {bookDetails.subjects ? bookDetails.subjects.join(', ') : 'Unknown'}</p>

          <h3>Recommendations</h3>
          <ul>
            {bookDetails.recommendations && bookDetails.recommendations.length > 0 ? (
              bookDetails.recommendations.map((recBook, index) => (
                <li key={index}>
                  <Link to={`/book/works/${recBook.key.replace('/works/', '')}`}>{recBook.title}</Link>
                </li>
              ))
            ) : (
              <p>No recommendations available</p>
            )}
          </ul>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default BookDetails;
