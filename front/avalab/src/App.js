import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProfileInside from './pages/profile/ProfileInside/ProfileInside';
import PersonalData from './pages/profile/PersonalData/PersonalData';

const App = () => {
    return (
        <Router>
          <Routes>
            {/* <Route path="/" element={<ProfileInside />} /> */}
            <Route path="/profile" element={<ProfileInside />}>
              <Route path="personal-data" element={<PersonalData />} />
            </Route>
          </Routes>
        </Router>
    );
};

export default App;


