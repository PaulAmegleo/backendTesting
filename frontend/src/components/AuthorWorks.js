import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

function AuthorWorks() {
  const { key } = useParams();
  const navigate = useNavigate();
  const [works, setWorks] = useState([]);

  useEffect(() => {
    const fetchAuthorWorks = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/api/author/${key}/works`);
        console.log('Response data:', response.data); // Log the response data
        setWorks(Array.isArray(response.data) ? response.data : []);
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
        {works.length > 0 ? (
          works.map((work, index) => (
            <li key={index} onClick={() => navigateToBookDetails(work.key)}>
              <Link to={`/book/works/${work.key.replace('/works/', '')}`}>{work.title}</Link>
            </li>
          ))
        ) : (
          <li>No works found for this author.</li>
        )}
      </ul>
    </div>
  );
}

export default AuthorWorks;
