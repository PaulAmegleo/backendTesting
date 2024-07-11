import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom'; // Import Link and useNavigate
import axios from 'axios';

function AuthorWorks() {
  const { key } = useParams();
  const navigate = useNavigate();
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

  const navigateToBookDetails = (workKey) => {
    navigate(`/book/works/${workKey.replace('/works/', '')}`); // Navigate to BookDetails route
  };

  return (
    <div>
      <h2>Author Works</h2>
      <ul>
        {works.map((work, index) => (
          <li key={index} onClick={() => navigateToBookDetails(work.key)}>
            <Link to={`/book/works/${work.key.replace('/works/', '')}`}>{work.title}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AuthorWorks;
