import React, { Component } from 'react';
import { Link } from 'react-router-dom'; // Используем react-router-dom

import styles from "./PersonalData.module.scss";
import SaveButton from '../../../components/SaveButton/SaveButton';

import leftAray from '../../../images/prof-perdata-img/Chevron left.svg';
import defaultAvatar from "../../../images/prof-perdata-img/image 3 (1).png";
import camera from "../../../images/prof-perdata-img/camera.svg";
import medalG from "../../../images/prof-perdata-img/medal.svg"
import medalS from "../../../images/prof-perdata-img/medal (1).svg"
import medalB from "../../../images/prof-perdata-img/medal (2).svg"
import trash from "../../../images/prof-perdata-img/trash.svg"
import close from "../../../images/prof-perdata-img/Vector.svg"
import x from "../../../images/prof-perdata-img/x.svg"
import plus from "../../../images/prof-perdata-img/plus.svg"

export default class PersonalData extends Component {
  constructor(props) {
    super(props);
    this.state = {
      avatarUrl: defaultAvatar, // URL аватара по умолчанию
      valueName: 'Иван', 
      valueSurname: "Иванов",
      valueUsername: '@0000001',
      valuePassword: '123456789',
      valueDateBorn: '01.01.2001',
      valuePhoneNumber: 'Отсутствует',
      valueStack: 'Html, CSS, JavaScrypt, React',
      editing: {
        valueName: false, 
        valueSurname: false,
        valueUsername: false,
        valuePassword: false,
        valueDateBorn: false,
        valuePhoneNumber: false,
        valueStack: false
      },
      isOpen: false,
      isOpenRole: false,

      addDis: true,
      addBack: false,
      addProduct: true, 
      addFull: false, 
      addAnal: true,
      addFront: false,
    };
    // Создаем ref для доступа к скрытому input
    this.fileInputRef = React.createRef();
    this.textareaRef = React.createRef();
  }

  // Программный клик по input
  buttonClick = () => {
    if (this.fileInputRef.current) {
      this.fileInputRef.current.click();
    }
  };

  // Обработка выбора файла
  fileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log("Выбранный файл:", file);
      const newAvatarUrl = URL.createObjectURL(file);
      this.setState({ avatarUrl: newAvatarUrl });
    }
  };

  // Переводим поле ввода в режим редактирования
  inputClick = (event) => {
    const {name} = event.target;
    this.setState(prevState => ({
      editing: {
        ...prevState.editing, [name]: true
      }
    }));
  };

  // Обновление значения при вводе
  inputChange = (event) => {
    const {name, value} = event.target
    this.setState({[name]: value });
  };

  // Сохранение введенного значения (выход из режима редактирования)
  saveInputClick = () => {
    this.setState(prevState => ({
      editing: Object.keys(prevState.editing).reduce((acc, key) => {
        acc[key] = false;
        return acc;
      }, {})
    }));
  };

  // Изменение высоты textarea
  changeHeight = () => {
    if (this.textareaRef.current) {
      this.textareaRef.current.style.height = 'auto';
      this.textareaRef.current.style.height = this.textareaRef.current.scrollHeight + 'px'
    }
  }

  // Изменеие значения textarea + смена высоты
  textareaChange = (event) => {
    const {name, value} = event.target
    this.setState({[name]: value});
    this.changeHeight();
  }

  // Запуск в первый рендеринг
  componentDidMount() {
    this.changeHeight();
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

  // Открытие панели ролей
  openRole = () => {
    this.setState({isOpenRole: true});
  }

  // Закрытие панели ролей
  closeRole = () => {
    this.setState({isOpenRole: false});
  }

  // Изменене статуса роли
  // roleClick = (event) => {
  //   const {name} = event.target
  //   this.setState({[name]: true});
  // }
  roleClick = (role) => {
    this.setState(prevState => ({
      [role]: !prevState[role] // Переключаем состояние: если было false, станет true, и наоборот
    }));
  }

  render() {
    return (
      <div className={styles.personalData}>
        <header className={styles.headerPersonalData}>
          <div className={styles.containerHeaderTop}>
            <Link to="/profile/">
              <img src={leftAray} alt="Back" />
            </Link>
            <p>Персональные данные</p>
          </div>
          <div className={styles.containerHeaderBottom}>
            <div className={styles.avatarContainer}>
              <img className={styles.avatar} src={this.state.avatarUrl} alt="Avatar" />
              <div className={styles.fileUploader}>
                <input 
                  type="file" 
                  ref={this.fileInputRef} 
                  onChange={this.fileChange}
                  style={{ display: 'none' }}
                />
                <button onClick={this.buttonClick}>
                  <img src={camera} alt="Upload" />
                </button>
              </div>
            </div>
            <p className={styles.name}>Иванов Иван</p>
            <p className={styles.email}>Ivanov@example.com</p>
          </div>
        </header>
        <div className={styles.headerOverlap}></div>

        <main className={styles.mainPersonalData}>
          <div className={`${styles.mainName} ${styles.shablon}`}>
            <span>Имя</span>
            <input 
              type="text" 
              name='valueName'
              value={this.state.valueName} 
              onClick={this.inputClick} 
              onChange={this.inputChange}
              readOnly={!this.state.editing.valueName}
            />
          </div>
          <div className={`${styles.mainSurname} ${styles.shablon}`}>
            <span>Фамилия</span>
            <input 
              type="text" 
              name='valueSurname'
              value={this.state.valueSurname} 
              onClick={this.inputClick} 
              onChange={this.inputChange}
              readOnly={!this.state.editing.valueSurname}
            />
          </div>
          <div className={`${styles.mainSurname} ${styles.shablon}`}>
            <span>Имя пользователя</span>
            <input 
              type="text" 
              name='valueUsername'
              value={this.state.valueUsername} 
              onClick={this.inputClick} 
              onChange={this.inputChange}
              readOnly={!this.state.editing.valueUsername}
            />
          </div>
          <div className={`${styles.mainSurname} ${styles.shablon}`}>
            <span>Пароль</span>
            <input 
              type="text" 
              name='valuePassword'
              value={this.state.valuePassword} 
              onClick={this.inputClick} 
              onChange={this.inputChange}
              readOnly={!this.state.editing.valuePassword}
            />
          </div>
          <div className={`${styles.mainSurname} ${styles.shablon}`}>
            <span>Достижения</span>
            <div className={styles.achievements}>
              <div className={styles.achievementsInside}>
                <img src={medalG}/>
                <span>99</span>
              </div>
              <div className={styles.achievementsInside}>
                <img src={medalS}/>
                <span>99</span>
              </div>
              <div className={styles.achievementsInside}>
                <img src={medalB}/>
                <span>99</span>
              </div>
            </div>
          </div>
          <div className={`${styles.mainSurname} ${styles.shablon}`}>
            <span>Дата рождения</span>
            <input 
              type="text" 
              name='valueDateBorn'
              value={this.state.valueDateBorn} 
              onClick={this.inputClick} 
              onChange={this.inputChange}
              readOnly={!this.state.editing.valueDateBorn}
            />
          </div>
          <div className={`${styles.mainSurname} ${styles.shablon}`}>
            <span>Телефон</span>
            <input 
              type="text" 
              name='valuePhoneNumber'
              value={this.state.valuePhoneNumber} 
              onClick={this.inputClick} 
              onChange={this.inputChange}
              readOnly={!this.state.editing.valuePhoneNumber}
            />
          </div>
          <div className={`${styles.mainSurname} ${styles.shablon}`}>
            <span>Стэк</span>
            <textarea
              type="text" 
              name='valueStack'
              ref={this.textareaRef}
              value={this.state.valueStack} 
              onClick={this.inputClick} 
              onChange={this.textareaChange}
              readOnly={!this.state.editing.valueStack}
              >
            </textarea> 
          </div>
          <div className={`${styles.rolesContainer} ${styles.shablon}`}>
            <span>Роль в команде</span>
            <div className={styles.rolesCont}>
              <div className={styles.roles}>
                <div className={styles.role} style={{display: !this.state.addDis ? 'none' : 'flex'}}>UI/UX Дизайнер</div>
                <div className={styles.role} style={{display: !this.state.addFront ? 'none' : 'flex'}}>Front-end</div>
                <div className={styles.role} style={{display: !this.state.addBack ? 'none' : 'flex'}}>Back-end</div>
                <div className={styles.role} style={{display: !this.state.addFull ? 'none' : 'flex'}}>FullStak</div>
                <div className={styles.role} style={{display: !this.state.addAnal ? 'none' : 'flex'}}>Аналитик</div>
                <div className={styles.role} style={{display: !this.state.addProduct ? 'none' : 'flex'}}>Project-manager</div>
              </div>
              <div className={styles.buttonPlus}>
                <button type='button' onClick={this.openRole} className={styles.plus}>+</button>
              </div>
            </div>
          </div>
          <div className={`${styles.deleteContainer} ${styles.shablon}`}>
            <span>Управление учетной записью</span>
            <button className={styles.delete} type="button" onClick={this.openMenu}>
              <img src={trash} alt="trash" />
              <span>Удалить аккаунт</span>
            </button>
          </div>
        </main>

       <SaveButton onClick={this.saveInputClick} />

       {this.state.isOpen && (
          <div className={styles.overlay} onClick={this.handleOverlayClick}>
            <div className={styles.deleteMenuPanel}>
              <div className={styles.deleteYes}>
                <div className={styles.deleteQuestion}>
                  <span>Вы точно хотите удалить аккаунт?</span>
                </div>
                <a href="#">Да</a>
              </div>
              <button className={styles.deleteNo} onClick={this.closeMenu}>
                Нет
              </button>
            </div>
          </div>
        )}

        {this.state.isOpenRole && (
          <div className={styles.overlay}>
            <div className={styles.rolePanel}>
              <div className={styles.rolePanelTop}>
                <p>Выберите роли</p>
                <button onClick={this.closeRole} className={styles.buttonClose}><img src={close} /></button>
              </div>
              <div className={styles.roleButtons}>
                <div name='addDis' onClick={() => this.roleClick('addDis')} className={styles.roleButton} >
                  <span>UI/UX Дизайнер</span>
                  <img src={!this.state.addDis ? plus : x} />
                </div>
                <div name='addBack' onClick={() => this.roleClick('addBack')} className={styles.roleButton}>
                  <span>Back-end </span>
                  <img src={!this.state.addBack ? plus : x} />
                </div>
                <div name='addProduct' onClick={() => this.roleClick('addProduct')} className={styles.roleButton}>
                  <span>Project-manager</span>
                  <img src={!this.state.addProduct ? plus : x} />
                </div>
                <div name='addFull' onClick={() => this.roleClick('addFull')} className={styles.roleButton}>
                  <span>Fullstack</span>
                  <img src={!this.state.addFull ? plus : x} />
                </div>
                <div name='addAnal' onClick={() => this.roleClick('addAnal')} className={styles.roleButton}>
                  <span>Аналитик</span>
                  <img src={!this.state.addAnal ? plus : x} />
                </div>
                <div name='addFront' onClick={() => this.roleClick('addFront')} className={styles.roleButton}>
                  <span>Front-end</span>
                  <img src={!this.state.addFront ? plus : x} />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }
}
