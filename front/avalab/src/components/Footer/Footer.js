import React, { Component } from 'react'
import { Link } from 'react-router';

import styles from "./footer.module.scss";

import home from "../../images/prof-inside-img/home-alt.svg";
import calendar from "../../images/prof-inside-img/calender.svg";
import chatFooter from "../../images/prof-inside-img/bx-chat.svg";
import userAct from "../../images/prof-inside-img/userAct.svg"

export default class Footer extends Component {
  render() {
    return (
        <footer className={styles.footerMain}>
          <div className={styles.footerContainer}>
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
    )
  }
}
