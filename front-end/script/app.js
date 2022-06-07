'use strict';
// #region ***  DOM references                           ***********
let htmlBoxOpen,
  htmlBoxClose,
  htmlBoxStatus,
  htmlHistoryToday,
  htmlHistoryAll,
  htmlLettersToday,
  htmlLidStatus,
  htmlIndex,
  htmlLogin,
  htmlAdd,
  htmlProfile,
  htmlEdit,
  htmlSettings,
  htmlUser,
  historyToday,
  historyAll,
  currentUser,
  token;

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
// #endregion

// #region ***  Callback-Visualisation - show___         ***********

const showHistoryToday = function (jsonObject) {
  // console.log(jsonObject.sensors);
  let stringHTML = '';
  for (const sensorInfo of jsonObject.sensors) {
    let datum = sensorInfo.date.split(' ');
    let tijdStip = datum[4];
    tijdStip = tijdStip.split(':');
    tijdStip = tijdStip[0] + ':' + tijdStip[1];
    stringHTML += `<tr>
                            <td>${tijdStip}</td>
                            <td>${sensorInfo.opmerking}</td>
                        </tr>`;
  }
  document.querySelector('.js-table').innerHTML = stringHTML;
};

const showHistoryAll = function (jsonObject) {
  // console.log(jsonObject);
  let stringHTML = '';
  for (const sensorInfo of jsonObject.sensors) {
    const datum = sensorInfo.date.split(' ');
    const showDatum = datum[1] + ' ' + datum[2] + ' ' + datum[3];
    stringHTML += `<tr>
                            <td>${showDatum}</td>
                            <td>${sensorInfo.opmerking}</td>
                        </tr>`;
  }
  document.querySelector('.js-table').innerHTML = stringHTML;
};

const showLidStatus = function (payload) {
  // console.log(payload.sensors);
  const status = payload.status.waarde;
  if (status == 0) {
    htmlLidStatus.innerHTML = `Closed`;
    htmlLidStatus.classList.remove('u-clr-main');
  } else {
    htmlLidStatus.innerHTML = `Opened`;
    htmlLidStatus.classList.add('u-clr-main');
  }
  let tijdStip = payload.status.date;
  tijdStip = tijdStip.split(' ');
  tijdStip = tijdStip[4];
  tijdStip = tijdStip.split(':');
  tijdStip = tijdStip[0] + ':' + tijdStip[1];
  document.querySelector('.js-lastLid').innerHTML = tijdStip;
};

const showLetters = function (payload) {
  // console.log(payload.letters[0].Aantal);
  htmlLettersToday.innerHTML = payload.letters[0].Aantal;
};

const showLatestLetter = function (payload) {
  // console.log(`Latest letter: ${payload.data.date}`);
  let datum = payload.data.date.split(' ');
  let tijdStip = datum[4];
  tijdStip = tijdStip.split(':');
  tijdStip = tijdStip[0] + ':' + tijdStip[1];
  document.querySelector('.js-lastDeposit').innerHTML = tijdStip;
};

const showLatestLock = function (payload) {
  // console.log(payload)
  if (payload.data.waarde == 1) {
    boxOpen();
  } else {
    boxClose();
  }
};

const showUsers = function (payload) {
  let stringHTML = ``;
  let rfid = '';
  let registreerdatum = '';
  for (const gebruiker of payload.gebruikers) {
    if (gebruiker.rfid_code != null) {
      rfid = `<svg xmlns="http://www.w3.org/2000/svg" width="32.55" height="23.5" viewBox="0 0 32.55 23.5">
            <path id="check_FILL0_wght400_GRAD0_opsz48"
                d="M18.9,35.7,7.7,24.5l2.15-2.15L18.9,31.4,38.1,12.2l2.15,2.15Z"
                transform="translate(-7.7 -12.2)" fill="#24d406" />
          </svg>`;
    } else {
      rfid = '--';
    }
    if (gebruiker.registreerdatum != null) {
      const datum = gebruiker.registreerdatum.split(' ');
      registreerdatum = datum[1] + ' ' + datum[2] + ' ' + datum[3];
    } else {
      registreerdatum = 'Unknown';
    }

    stringHTML += `
      <tr>
        <td class="u-pd-rght-l">${gebruiker.naam}</td>
        <td class="u-pd-rght-s">
            ${rfid}
        </td>
        <td class="u-pd-rght-m">${registreerdatum}</td>
        <td class="u-pd-rght-xs js-removeuser" data-userid="${gebruiker.gebruikersID}">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="36" viewBox="0 0 32 36">
                <path id="delete_FILL0_wght400_GRAD0_opsz48_1_"
                    data-name="delete_FILL0_wght400_GRAD0_opsz48 (1)"
                    d="M13.05,42a3.076,3.076,0,0,1-3-3V10.5H8v-3h9.4V6H30.6V7.5H40v3H37.95V39a3.076,3.076,0,0,1-3,3Zm21.9-31.5H13.05V39h21.9ZM18.35,34.7h3V14.75h-3Zm8.3,0h3V14.75h-3ZM13.05,10.5V39h0Z"
                    transform="translate(-8 -6)" />
            </svg>
        </td>
        <td class="u-pd-rght-xs js-edit">
          <a href="edit.html?userID=${gebruiker.gebruikersID}">
              <svg xmlns="http://www.w3.org/2000/svg" width="36.65" height="36.626"
                  viewBox="0 0 36.65 36.626">
                  <path id="edit_FILL0_wght400_GRAD0_opsz48_2_"
                      data-name="edit_FILL0_wght400_GRAD0_opsz48 (2)"
                      d="M9,39h2.2L35.45,14.75l-1.1-1.1-1.1-1.1L9,36.8ZM6,42V35.6L35.4,6.2a2.8,2.8,0,0,1,2.125-.825,2.971,2.971,0,0,1,2.125.875L41.8,8.4a2.853,2.853,0,0,1,.85,2.1,2.853,2.853,0,0,1-.85,2.1L12.4,42ZM39.5,10.45,37.45,8.4Zm-4.05,4.3-1.1-1.1-1.1-1.1Z"
                      transform="translate(-6 -5.374)" />
              </svg>
            </a>
        </td>
      </tr>`;
  }
  document.querySelector('.js-tableUsers').innerHTML = stringHTML;
  listenToDeleteUser();
};

const showUserInfo = function (payload) {
  // console.log(payload);
  let registreerdatum = '';
  if (payload.gebruikers.registreerdatum != null) {
    const datum = payload.gebruikers.registreerdatum.split(' ');
    registreerdatum = datum[1] + ' ' + datum[2] + ' ' + datum[3];
  } else {
    registreerdatum = 'Unknown';
  }
  document.querySelector('.js-name').innerHTML = payload.gebruikers.naam;
  setValueAndId('js-parRfid', payload.gebruikers.rfid_code);
  setValueAndId('js-parName', payload.gebruikers.naam);
  setValueAndId('js-parPwrd', payload.gebruikers.wachtwoord);
  setValueAndId('js-parRegDate', registreerdatum);
  listenToUpdateUser();
};

const showRFIDInfo = function (payload) {
  // console.log('YEEY');
  setValueAndId('js-parRfid', payload.rfid);
};

const callbackShow = function (jsonObj) {
  // console.log(jsonObj.logged_in_as.gebruikersID);
  sessionStorage.setItem('currentUser', jsonObj.logged_in_as.gebruikersID);
  currentUser = jsonObj.logged_in_as.gebruikersID;
  window.location.href = 'home.html';
};

const showloginError = function (jsonObj) {
  console.log(jsonObj);
};

const callbackError = function (jsonObj) {
  console.log(jsonObj);
};

const showSucces = function (jsonObj) {
  document.querySelector(
    '.js-truncateResult'
  ).innerHTML = `Data succesfully removed`;
};

const showLastLetters = function (jsonObj) {
  // console.log(jsonObj);
  if (jsonObj.letters.Aantal > 0) {
    document.querySelector(
      '.js-latestLetterCount'
    ).innerHTML = `<span class="c-dot u-bgclr-main"></span> You have unchecked post!`;
  } else {
    document.querySelector(
      '.js-latestLetterCount'
    ).innerHTML = `<span class="c-dot"></span> No post currently in your mailbox.`;
  }
};
// #endregion

// #region ***  Callback-No Visualisation - callback___  ***********
const setValueAndId = function (jsKlasse, value) {
  document.querySelector(`.${jsKlasse}`).setAttribute('value', value);
  document.querySelector(`.${jsKlasse}`).setAttribute('id', value);
};

const backToList = function (jsonObj) {
  window.location.href = 'users.html';
};

const boxOpen = function () {
  htmlBoxOpen.classList.remove('c-btn--unselected');
  htmlBoxOpen.classList.add('c-btn--selected');
  htmlBoxOpen.classList.add('u-no-clicking');
  htmlBoxOpen.innerHTML = 'Unlocked';
  // other element
  htmlBoxClose.classList.add('c-btn--unselected');
  htmlBoxClose.classList.remove('c-btn--selected');
  htmlBoxClose.classList.remove('u-no-clicking');
  htmlBoxStatus.innerHTML = 'Open';
  htmlBoxStatus.classList.add('u-clr-main');
  htmlBoxClose.innerHTML = 'Close';
};

const boxClose = function () {
  htmlBoxClose.classList.remove('c-btn--unselected');
  htmlBoxClose.classList.add('c-btn--selected');
  htmlBoxClose.classList.add('u-no-clicking');
  htmlBoxClose.innerHTML = 'Locked';
  // other element
  htmlBoxOpen.classList.add('c-btn--unselected');
  htmlBoxOpen.classList.remove('c-btn--selected');
  htmlBoxOpen.classList.remove('u-no-clicking');
  htmlBoxStatus.innerHTML = 'Closed';
  htmlBoxStatus.classList.remove('u-clr-main');
  htmlBoxOpen.innerHTML = 'Open';
};

const LoginAcces = function (jsonObj) {
  token = jsonObj.access_token;
  console.log(token);
  handleData(
    `http://${lanIP}/api/v1/protected/`,
    callbackShow,
    callbackError,
    'GET',
    null,
    token
  );
};

const setCurrentUser = function () {
  currentUser = sessionStorage.getItem('currentUser');
  document
    .querySelector('.js-currentUser')
    .setAttribute('href', `profile.html?userID=${currentUser}`);
};
// #endregion

// #region ***  Data Access - get___                     ***********
const loadHistoryToday = function () {
  const url = `http://192.168.168.169:5000/api/v1/events/today/`;
  handleData(url, showHistoryToday);
};

const loadHistoryAll = function () {
  const url = `http://192.168.168.169:5000/api/v1/events/`;
  handleData(url, showHistoryAll);
};

const loadLidStatus = function () {
  const url = `http://192.168.168.169:5000/api/v1/events/lid/`;
  handleData(url, showLidStatus);
};

const loadLettersToday = function () {
  const url = `http://192.168.168.169:5000/api/v1/events/letters/`;
  handleData(url, showLetters);
};

const loadLatestLetter = function () {
  const url = `http://192.168.168.169:5000/api/v1/events/letters/latest/`;
  handleData(url, showLatestLetter);
};

const loadLatestLock = function () {
  const url = `http://192.168.168.169:5000/api/v1/events/lock/latest/`;
  handleData(url, showLatestLock);
};

const getUsers = function () {
  const url = `http://192.168.168.169:5000/api/v1/users/`;
  handleData(url, showUsers);
};

const getUserInfo = function (UserID) {
  const url = `http://192.168.168.169:5000/api/v1/user/${UserID}/`;
  handleData(url, showUserInfo);
};

const getLatestLetters = function () {
  const url = `http://192.168.168.169:5000/api/v1/events/letters/count/`;
  handleData(url, showLastLetters);
};
// #endregion

// #region ***  Event Listeners - listenTo___            ***********
const listenToUIIndex = function () {
  // togle box lock
  htmlBoxOpen.addEventListener('click', function () {
    if (currentUser != null) {
      console.log('Setting box Unlocked');
      boxOpen();
      socket.emit('F2B_openBox', { userID: currentUser });
    }
  });
  htmlBoxClose.addEventListener('click', function () {
    if (currentUser != null) {
      console.log('Setting box Locked');
      boxClose();
      socket.emit('F2B_closeBox', { userID: currentUser });
    }
  });

  // toggle history showings
  htmlHistoryToday.addEventListener('click', function () {
    console.log('Showing today');
    this.classList.remove('c-btn--unselected');
    this.classList.add('c-btn--selected');
    // other element
    htmlHistoryAll.classList.add('c-btn--unselected');
    htmlHistoryAll.classList.remove('c-btn--selected');
    // setting globals
    historyToday = true;
    historyAll = false;
    // load history
    loadHistoryToday();
  });
  htmlHistoryAll.addEventListener('click', function () {
    console.log('Showing all');
    this.classList.remove('c-btn--unselected');
    this.classList.add('c-btn--selected');
    // other element
    htmlHistoryToday.classList.add('c-btn--unselected');
    htmlHistoryToday.classList.remove('c-btn--selected');
    // setting globals
    historyToday = false;
    historyAll = true;
    // load history
    loadHistoryAll();
  });
};

const listenToSocket = function () {
  socket.on('connected', function () {
    console.log('verbonden met socket webserver');
  });
  socket.on('B2F_new_letter', function () {
    getLatestLetters();
    loadLatestLetter();
  });
  socket.on('B2F_emptyd_letters', function () {
    getLatestLetters();
  });
};

const listenToSocketIndex = function () {
  socket.on('B2F_change_magnet', function (payload) {
    loadLidStatus();
  });
  socket.on('B2F_refresh_history', function (payload) {
    if (historyAll == true) {
      loadHistoryAll();
    } else {
      loadHistoryToday();
    }
  });
  socket.on('B2F_changed_lock', function (payload) {
    // console.log(payload);
    const lock_status = payload.lock_status;
    if (lock_status == true) {
      boxOpen();
    } else {
      boxClose();
    }
  });
};

const listenToSocketAdd = function () {
  socket.on('B2F_rfidwritten', function (payload) {
    showRFIDInfo(payload);
  });
};

const listenToSocketLogin = function () {
  socket.on('B2F_loginPermitted', function (payload) {
    sessionStorage.setItem('currentUser', payload.userID);
    window.location.href = 'home.html';
  });
};

const listenToUpdateUser = function () {
  document
    .querySelector('.js-updateuser')
    .addEventListener('click', function () {
      const rfid = document.querySelector('.js-parRfid').value;
      const name = document.querySelector('.js-parName').value;
      const pwrd = document.querySelector('.js-parPwrd').value;
      const body = JSON.stringify({
        rfid: rfid,
        naam: name,
        wachtwoord: pwrd,
      });
      let urlParams = new URLSearchParams(window.location.search);
      let userID = urlParams.get('userID');
      const url = `http://192.168.168.169:5000/api/v1/user/${userID}/`;
      handleData(url, backToList, null, 'PUT', body);
    });
};

const listenToDeleteUser = function () {
  const btns = document.querySelectorAll('.js-removeuser');
  for (const btn of btns) {
    btn.addEventListener('click', function () {
      // console.log('click');
      const userID = this.dataset.userid;
      // console.log(userID);
      const url = `http://192.168.168.169:5000/api/v1/user/${userID}/`;
      handleData(url, backToList, null, 'DELETE');
    });
  }
};

const listenToSubmit = function () {
  document.querySelector('.js-adduser').addEventListener('click', function () {
    const rfid = document.querySelector('.js-parRfid').value;
    const name = document.querySelector('.js-parName').value;
    const pwrd = document.querySelector('.js-parPwrd').value;
    if (name == '') {
      document.querySelector('.js-parName').classList.add('u-bdclr-red');
    } else if (pwrd == '') {
      document.querySelector('.js-parPwrd').classList.add('u-bdclr-red');
    } else {
      let body = JSON.stringify({
        rfid: rfid,
        naam: name,
        wachtwoord: pwrd,
      });
      const url = `http://192.168.168.169:5000/api/v1/users/`;
      handleData(url, backToList, null, 'POST', body);
      console.log('verzonden');
    }
  });
};

const listenToToggleNav = function () {
  const btns = document.querySelectorAll('.js-toggle-nav');
  for (const btn of btns) {
    btn.addEventListener('click', function () {
      document.querySelector('body').classList.toggle('has-mobile-nav');
    });
  }
};

const listenToLogin = function () {
  document.querySelector('.js-login').addEventListener('click', function () {
    const body = JSON.stringify({
      username: document.querySelector('.js-userName').value,
      password: document.querySelector('.js-passWord').value,
    });
    handleData(
      `http://${lanIP}/api/v1/login/`,
      LoginAcces,
      showloginError,
      'POST',
      body
    );
  });
};

const listenToReset = function () {
  document.querySelector('.js-reset').addEventListener('click', function () {
    if (confirm('Delete all records?')) {
      handleData(`http://${lanIP}/api/v1/events/`, showSucces, null, 'DELETE');
    } else {
    }
  });
};

const listenToLogout = function () {
  document.querySelector('.js-logout').addEventListener('click', function () {
    sessionStorage.setItem('currentUser', '');
    currentUser = '';
    window.location.href = 'index.html';
  });
};
// #endregion

// #region ***  Init / DOMContentLoaded                  ***********
const init = function () {
  console.info('DOM geladen');

  // Select pages
  htmlIndex = document.querySelector('.js-indexPage');
  htmlUser = document.querySelector('.js-userPage');
  htmlEdit = document.querySelector('.js-editPage');
  htmlAdd = document.querySelector('.js-addPage');
  htmlLogin = document.querySelector('.js-loginPage');
  htmlSettings = document.querySelector('.js-settingsPage');
  htmlProfile = document.querySelector('.js-profilePage');

  // execute when correct page
  if (htmlIndex) {
    htmlBoxOpen = document.querySelector('.js-boxopen');
    htmlBoxClose = document.querySelector('.js-boxclose');
    htmlHistoryToday = document.querySelector('.js-historytoday');
    htmlHistoryAll = document.querySelector('.js-historyall');
    htmlLidStatus = document.querySelector('.js-lid');
    htmlLettersToday = document.querySelector('.js-brievenaantal');
    htmlBoxStatus = document.querySelector('.js-lockStatus');
    setCurrentUser();
    loadHistoryToday();
    loadLidStatus();
    loadLettersToday();
    loadLatestLetter();
    loadLatestLock();
    listenToUIIndex();
    listenToSocketIndex();
  } else if (htmlEdit) {
    let urlParams = new URLSearchParams(window.location.search);
    let userID = urlParams.get('userID');
    if (userID) {
      setCurrentUser();
      getUserInfo(userID);
    } else {
      window.location.href = 'home.html';
    }
  } else if (htmlUser) {
    setCurrentUser();
    getUsers();
  } else if (htmlAdd) {
    socket.emit('F2B_waitingForRegister');
    listenToSubmit();
    listenToSocketAdd();
  } else if (htmlLogin) {
    socket.emit('F2B_waitingForLogin');
    listenToLogin();
    listenToSocketLogin();
  } else if (htmlSettings) {
    setCurrentUser();
    listenToReset();
  } else if (htmlProfile) {
    let urlParams = new URLSearchParams(window.location.search);
    let userID = urlParams.get('userID');
    if (userID) {
      console.log(userID);
      setCurrentUser();
      getUserInfo(userID);
      listenToLogout();
    } else {
      window.location.href = 'home.html';
    }
  }

  // event listeners and loads
  getLatestLetters();
  setCurrentUser();
  listenToSocket();
  listenToToggleNav();
};

document.addEventListener('DOMContentLoaded', init);
// #endregion
