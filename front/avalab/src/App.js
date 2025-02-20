import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProfileLayout from './pages/profile/ProfileLayout';


const App = () => {
    return (
        <Router>
          <Routes>
            {/* <Route path="/" element={<ProfileInside />} /> */}
            <Route path='/profile/*' element={<ProfileLayout />}/>
          </Routes>
        </Router>
    );
};

export default App;


