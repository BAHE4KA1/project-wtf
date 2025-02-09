import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ProfileInside from "./ProfileInside/ProfileInside";
import PersonalData from "./PersonalData/PersonalData";

const ProfileLayout = () => {
  return (
    <Routes>
      <Route index element={<ProfileInside />} />
      <Route path="personal-data" element={<PersonalData />} /> 
    </Routes>
  );
};

export default ProfileLayout;
