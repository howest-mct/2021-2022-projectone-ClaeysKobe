'use strict';
let htmlBoxOpen, htmlBoxClose, htmlHistoryToday, htmlHistoryAll, htmlLidStatus, historyToday, historyAll

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

const showHistoryToday = function(jsonObject) {
  // console.log(jsonObject.sensors);
  let stringHTML = '';
  for (const sensorInfo of jsonObject.sensors){
    const datum = sensorInfo.date.split(' ')
    stringHTML += `<tr>
                            <td>${datum[4]}</td>
                            <td>${sensorInfo.opmerking}</td>
                        </tr>`
  }
  document.querySelector('.js-table').innerHTML = stringHTML;
};

const showHistoryAll = function(jsonObject) {
  // console.log(jsonObject);
  let stringHTML = '';
  for (const sensorInfo of jsonObject.sensors){
    const datum = sensorInfo.date.split(' ')
    const showDatum = datum[1] + ' ' + datum[2] + ' ' + datum[3]
    stringHTML += `<tr>
                            <td>${showDatum}</td>
                            <td>${sensorInfo.opmerking}</td>
                        </tr>`
  }
  document.querySelector('.js-table').innerHTML = stringHTML;
}

const showLidStatus = function(payload) {
  if (payload.status == 0) {
    htmlLidStatus.innerHTML = `Gesloten`
    htmlLidStatus.classList.remove('u-clr-main');
  }
  else {
    htmlLidStatus.innerHTML = `Geopend`
    htmlLidStatus.classList.add('u-clr-main');
  }
}

const loadHistoryToday = function () {
  const url = `http://192.168.168.169:5000/api/v1/sensors/today/`;
  handleData(url, showHistoryToday);
};

const loadHistoryAll = function () {
  const url = `http://192.168.168.169:5000/api/v1/sensors/`;
  handleData(url, showHistoryAll);
}

const loadLidStatus = function () {
  const url = `http://192.168.168.169:5000/api/v1/sensors/lid/`
  handleData(url,showLidStatus)
}

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
      socket.emit('F2B_openBox')
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
      socket.emit('F2B_closeBox')
    })

    // toggle history showings
    htmlHistoryToday.addEventListener('click', function () {
      console.log('Showing today');
      this.classList.remove('c-btn--unselected')
      this.classList.add('c-btn--selected');
      // other element
      htmlHistoryAll.classList.add('c-btn--unselected');
      htmlHistoryAll.classList.remove('c-btn--selected');
      // setting globals
      historyToday = true;
      historyAll = false;
      // load history
      loadHistoryToday();
    })
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
    })
};

const listenToSocket = function () {
  socket.on('connected', function () {
    console.log("verbonden met socket webserver");
  });
  socket.on('B2F_change_magnet', function (payload) {
    showLidStatus(payload)
  })
  socket.on('B2F_refresh_history', function (payload) {
    if (historyAll == true) {
      loadHistoryAll();
    } else {
      loadHistoryToday();
    }
  })
};

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  htmlBoxOpen = document.querySelector('.js-boxopen');
  htmlBoxClose = document.querySelector('.js-boxclose');
  htmlHistoryToday = document.querySelector('.js-historytoday');
  htmlHistoryAll = document.querySelector('.js-historyall');
  htmlLidStatus = document.querySelector('.js-lid')
  listenToUI();
  listenToSocket();
  loadHistoryToday();
  loadLidStatus()
});
