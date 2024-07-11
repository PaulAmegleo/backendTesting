// BookList.js
import React from 'react';
import { Link } from 'react-router-dom';

const BookList = ({ books }) => {
    return (
        <div>
            {books.map(book => (
                <div key={book.key}>
                    <h2>{book.title}</h2>
                    <Link to={`/works/${book.key}`}>
                        <img src={book.cover_image} alt={`${book.title} cover`} />
                    </Link>
                </div>
            ))}
        </div>
    );
};

export default BookList;
