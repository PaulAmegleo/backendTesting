import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import SearchResults from './components/SearchResults';
import BookDetails from './components/BookDetails';
import AuthorWorks from './components/AuthorWorks';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="/book/works/:key" element={<BookDetails />} />
          <Route path="/author/:key" element={<AuthorWorks />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
