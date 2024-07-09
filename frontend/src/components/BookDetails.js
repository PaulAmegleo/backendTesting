import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function BookDetails() {
  const { key } = useParams();
  const [book, setBook] = useState(null);

  useEffect(() => {
    const fetchBookDetails = async () => {
      try {
        const response = await axios.get(`/book/${key}`);
        setBook(response.data);
      } catch (error) {
        console.error('Error fetching book details:', error);
      }
    };

    fetchBookDetails();
  }, [key]);

  if (!book) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>{book.title}</h2>
      <p>Author: {book.authors && book.authors.map(author => author.name).join(', ')}</p>
      <p>First published: {book.first_publish_year}</p>
      <p>Description: {typeof book.description === 'object' ? book.description.value : book.description}</p>
      {book.cover_image && (
        <img src={book.cover_image} alt={`${book.title} cover`} />
      )}
      <p>Ratings: {book.ratings}</p>
    </div>
  );
}

export default BookDetails;
