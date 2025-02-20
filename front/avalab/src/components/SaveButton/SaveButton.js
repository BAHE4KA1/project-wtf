import React, { Component } from 'react'

import styles from "./SaveButton.module.scss";

export default class SaveButton extends Component {
  render() {

    const {onSave} = this.props;

    return (
        <footer className={styles.saveButton}>
            <button onClick={onSave}>Сохранить</button>
        </footer>
    )
  }
}
