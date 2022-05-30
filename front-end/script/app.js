'use strict';
// #region ***  DOM references                           ***********
let htmlBoxOpen,
  htmlBoxClose,
  htmlHistoryToday,
  htmlHistoryAll,
  htmlLettersToday,
  htmlLidStatus,
  htmlIndex,
  htmlAdd,
  htmlEdit,
  htmlUser,
  historyToday,
  historyAll;

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
// #endregion

// #region ***  Callback-Visualisation - show___         ***********

const showHistoryToday = function (jsonObject) {
  // console.log(jsonObject.sensors);
  let stringHTML = '';
  for (const sensorInfo of jsonObject.sensors) {
    const datum = sensorInfo.date.split(' ');
    stringHTML += `<tr>
                            <td>${datum[4]}</td>
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
  if (payload.status == 0) {
    htmlLidStatus.innerHTML = `Gesloten`;
    htmlLidStatus.classList.remove('u-clr-main');
  } else {
    htmlLidStatus.innerHTML = `Geopend`;
    htmlLidStatus.classList.add('u-clr-main');
  }
};

const showLetters = function (payload) {
  console.log(payload.sensors);
  if (payload.sensors > 1) {
    htmlLettersToday.innerHTML = payload.sensors;
  } else if (payload.sensors == 1) {
    htmlLettersToday.innerHTML = '1 brief';
  } else {
    htmlLettersToday.innerHTML = '-- brieven';
  }
};

const showUsers = function (payload) {
  let stringHTML = ``;
  let rfid = '';
  for (const gebruiker of payload.gebruikers) {
    if (gebruiker.rfid_code != null) {
      rfid = 'Yes';
    } else {
      rfid = 'No';
    }
    stringHTML += `
    <tr>
        <td>${rfid}</td>
        <td>${gebruiker.naam}</td>
        <td class="js-edit">
            <a href="edit.html?userID=${gebruiker.gebruikersID}">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path id="edit_FILL1_wght400_GRAD0_opsz48"
                  d="M27.34,10.812,23.288,6.76l2.66-2.66L30,8.153ZM6,28.1V24.047L21.958,8.089l4.053,4.053L10.053,28.1Z"
                  transform="translate(-6 -4.1)" />
              </svg>
            </a>
        </td>
    </tr>`;
  }
  document.querySelector('.js-tableUsers').innerHTML = stringHTML;
};
// #endregion

// #region ***  Callback-No Visualisation - callback___  ***********
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

const getUsers = function () {
  const url = `http://192.168.168.169:5000/api/v1/users/`;
  handleData(url, showUsers);
};
// #endregion

// #region ***  Event Listeners - listenTo___            ***********
const listenToUI = function () {
  // togle box lock
  htmlBoxOpen.addEventListener('click', function () {
    console.log('Setting box Unlocked');
    this.classList.remove('c-btn--unselected');
    this.classList.add('c-btn--selected');
    this.classList.add('u-no-clicking');
    // other element
    htmlBoxClose.classList.add('c-btn--unselected');
    htmlBoxClose.classList.remove('c-btn--selected');
    htmlBoxClose.classList.remove('u-no-clicking');
    socket.emit('F2B_openBox');
  });
  htmlBoxClose.addEventListener('click', function () {
    console.log('Setting box Locked');
    this.classList.remove('c-btn--unselected');
    this.classList.add('c-btn--selected');
    this.classList.add('u-no-clicking');
    // other element
    htmlBoxOpen.classList.add('c-btn--unselected');
    htmlBoxOpen.classList.remove('c-btn--selected');
    htmlBoxOpen.classList.remove('u-no-clicking');
    socket.emit('F2B_closeBox');
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
  socket.on('B2F_change_magnet', function (payload) {
    showLidStatus(payload);
  });
  socket.on('B2F_refresh_history', function (payload) {
    if (historyAll == true) {
      loadHistoryAll();
    } else {
      loadHistoryToday();
    }
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

  // execute when correct page
  if (htmlIndex) {
    htmlBoxOpen = document.querySelector('.js-boxopen');
    htmlBoxClose = document.querySelector('.js-boxclose');
    htmlHistoryToday = document.querySelector('.js-historytoday');
    htmlHistoryAll = document.querySelector('.js-historyall');
    htmlLidStatus = document.querySelector('.js-lid');
    htmlLettersToday = document.querySelector('.js-brievenaantal');
    loadHistoryToday();
    loadLidStatus();
    loadLettersToday();
  } else if (htmlEdit) {
    let urlParams = new URLSearchParams(window.location.search);
    let userID = urlParams.get('userID');
    if (userID) {
      getUserInfo(userID);
    } else {
      window.location.href = 'index.html';
    }
  } else if (htmlUser) {
    getUsers();
  }

  // event listeners and loads
  listenToUI();
  listenToSocket();
};

document.addEventListener('DOMContentLoaded', init);
// #endregion
