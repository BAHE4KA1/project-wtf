import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProfileInside from './pages/profile/ProfileInside/ProfileInside';
import ProfileLayout from './pages/profile/ProfileLayout';

const App = () => {
    return (
        <Router>
          <Routes>
            {/* <Route path="/" element={<ProfileInside />} /> */}
            <Route path="/profile/*" element={<ProfileInside />} />
          </Routes>
        </Router>
    );
};

export default App;


