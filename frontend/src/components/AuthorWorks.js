import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function AuthorWorks() {
  const { key } = useParams();
  const [works, setWorks] = useState([]);

  useEffect(() => {
    const fetchAuthorWorks = async () => {
      try {
        const response = await axios.get(`https://openlibrary.org/authors/${key}/works.json`);
        setWorks(response.data.entries || []);
      } catch (error) {
        console.error('Error fetching author works:', error);
      }
    };

    fetchAuthorWorks();
  }, [key]);

  return (
    <div>
      <h2>Author Works</h2>
      <ul>
        {works.map((work, index) => (
          <li key={index}>
            {work.title}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AuthorWorks;
