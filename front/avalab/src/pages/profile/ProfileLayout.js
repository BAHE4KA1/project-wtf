import React from "react";
import { useRoutes, Outlet } from "react-router-dom";
import ProfileInside from "./ProfileInside/ProfileInside";
import PersonalData from "./PersonalData/PersonalData";


const ProfileLayout = () => {

  const routes = [
    { path: '/', element: <ProfileInside />},
    { path: "personal-data", element: <PersonalData /> }
  ];

  const element = useRoutes(routes);

  return (
    <>
    {element}
    </>
  );
};

export default ProfileLayout;
