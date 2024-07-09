import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('title');
  const navigate = useNavigate();

  const handleSearch = () => {
    navigate(`/search?query=${query}&type=${searchType}`);
  };

  return (
    <div>
      <h1>Reader's Realm</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={`Enter ${searchType} to search`}
      />
      <select value={searchType} onChange={(e) => setSearchType(e.target.value)}>
        <option value="title">Title</option>
        <option value="author">Author</option>
      </select>
      <button onClick={handleSearch}>Search</button>
    </div>
  );
}

export default Home;
