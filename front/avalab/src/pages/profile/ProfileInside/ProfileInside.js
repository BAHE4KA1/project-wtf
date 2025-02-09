import React, { Component } from 'react';
import { Link, Routes, Route } from "react-router-dom";

import "./ProfileInside.css";
import PersonalData from '../PersonalData/PersonalData';

import image3 from "../../../images/prof-inside-img/image 3.png";
import user from "../../../images/prof-inside-img/user.svg";
import arrow from "../../../images/prof-inside-img/Chevron right.svg";
import email from "../../../images/prof-inside-img/email-security.svg";
import userAlt from "../../../images/prof-inside-img/users-alt.svg";
import chat from "../../../images/prof-inside-img/chat-left-dots.svg";
import help from "../../../images/prof-inside-img/help.svg";
import exit from "../../../images/prof-inside-img/bx-log-out.svg";
import home from "../../../images/prof-inside-img/home-alt.svg";
import calendar from "../../../images/prof-inside-img/calender.svg";
import chatFooter from "../../../images/prof-inside-img/bx-chat.svg";
import userAct from "../../../images/prof-inside-img/userAct.svg";

export default class ProfileInside extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isOpen: false, // Состояние для модального окна
    };
  }

  openMenu = () => {
    this.setState({ isOpen: true });
  };

  closeMenu = () => {
    this.setState({ isOpen: false });
  };

  handleOverlayClick = (event) => {
    if (event.target.classList.contains("overlay")) {
      this.closeMenu();
    }
  };

  render() {
    return (
      <div className="ProfileInside">
        <header className="header-ProfileInside">
          <div className="header-container">
            <img src={image3} alt="Аватар" />
            <p className="name">Иванов Иван</p>
            <p className="email">Ivanov@example.com</p>
          </div>
        </header>

        <main>
          <div className="main-buttons">
            <Link to="personal-data">
              <div className="button-left">
                <img src={user} alt="User" />
                <span>Персональные данные</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
            <Link to="/profile/privacy">
              <div className="button-left">
                <img src={email} alt="Email" />
                <span>Приватность и уведомления</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
            <Link to="/profile/teams">
              <div className="button-left">
                <img src={userAlt} alt="User Alt" />
                <span>Мои команды</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
            <Link to="/profile/chat">
              <div className="button-left">
                <img src={chat} alt="Chat" />
                <span>Чат поддержки</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
            <Link to="/profile/help">
              <div className="button-left">
                <img src={help} alt="Help" />
                <span>Справка</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
          </div>

          <button className="exit" type="button" onClick={this.openMenu}>
            <img src={exit} alt="exit" />
            <span>Выйти из аккаунта</span>
          </button>
        </main>

        <footer>
          <div className="footer-container">
            <Link to="/home">
              <img src={home} alt="home" />
            </Link>
            <Link to="/calendar">
              <img src={calendar} alt="calendar" />
            </Link>
            <Link to="/chat">
              <img src={chatFooter} alt="chatFooter" />
            </Link>
            <Link to="/profile">
              <img src={userAct} alt="userAct" />
            </Link>
          </div>
        </footer>

        {this.state.isOpen && (
          <div className="overlay" onClick={this.handleOverlayClick}>
            <div className="exitMenuPanel">
              <div className="exitYes">
                <div className='exitQuestion'><span>Вы точно хотите выйти из аккаунта?</span></div>
                <a href="#">Да</a>
              </div>
              <button className="exitNo" onClick={this.closeMenu}>
                Нет
              </button>
            </div>
          </div>
        )}

        <Routes>
          <Route path="personal-data" element={<PersonalData />} />
        </Routes>
      </div>
    );
  }
}
