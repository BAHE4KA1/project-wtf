import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import styles from "./ProfileInside.module.scss";
import Footer from "../../../components/Footer/Footer";

import image3 from "../../../images/prof-inside-img/image 3.png";
import user from "../../../images/prof-inside-img/user.svg";
import arrow from "../../../images/prof-inside-img/Chevron right.svg";
import email from "../../../images/prof-inside-img/email-security.svg";
import userAlt from "../../../images/prof-inside-img/users-alt.svg";
import chat from "../../../images/prof-inside-img/chat-left-dots.svg";
import help from "../../../images/prof-inside-img/help.svg";
import exit from "../../../images/prof-inside-img/bx-log-out.svg";

export default class ProfileInside extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isOpen: false,
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
      <div className={styles.profileInside}>
        <header className={styles.headerProfileInside}>
          <div className={styles.headerContainer}>
            <Link to='/profile/'>
              <img src={image3} alt="Аватар" />
            </Link>
            <p className={styles.name}>Иванов Иван</p>
            <p className={styles.email}>Ivanov@example.com</p>
          </div>
        </header>

        <main className={styles.mainProfileInside}>
          <div className={styles.mainButtons}>
            <Link to="personal-data">
              <div className={styles.buttonLeft}>
                <img src={user} alt="User" />
                <span>Персональные данные</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
            <Link to="/profile/privacy">
              <div className={styles.buttonLeft}>
                <img src={email} alt="Email" />
                <span>Приватность и уведомления</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
            <Link to="/profile/teams">
              <div className={styles.buttonLeft}>
                <img src={userAlt} alt="User Alt" />
                <span>Мои команды</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
            <Link to="/profile/chat">
              <div className={styles.buttonLeft}>
                <img src={chat} alt="Chat" />
                <span>Чат поддержки</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
            <Link to="/profile/help">
              <div className={styles.buttonLeft}>
                <img src={help} alt="Help" />
                <span>Справка</span>
              </div>
              <img src={arrow} alt="Arrow" />
            </Link>
          </div>

          <button className={styles.exit} type="button" onClick={this.openMenu}>
            <img src={exit} alt="exit" />
            <span>Выйти из аккаунта</span>
          </button>
        </main>

        <Footer />

        {this.state.isOpen && (
          <div className={styles.overlay} onClick={this.handleOverlayClick}>
            <div className={styles.exitMenuPanel}>
              <div className={styles.exitYes}>
                <div className={styles.exitQuestion}>
                  <span>Вы точно хотите выйти из аккаунта?</span>
                </div>
                <a href="#">Да</a>
              </div>
              <button className={styles.exitNo} onClick={this.closeMenu}>
                Нет
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }
}
