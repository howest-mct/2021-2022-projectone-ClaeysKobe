'use strict';
let htmlBoxOpen, htmlBoxClose, htmlHistoryToday, htmlHistoryAll

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

const showHistory = function(jsonObject) {
  console.log(jsonObject);
  let stringHTML = '';
  for (const sensorInfo of jsonObject.sensors){
    stringHTML += `<tr>
                            <td>${sensorInfo.actiedatum}</td>
                            <td>${sensorInfo.waarde}</td>
                        </tr>`
  }
  document.querySelector('.js-table').innerHTML = stringHTML;
};

const loadHistoryToday = function () {
  const url = `http://192.168.168.169:5000/api/v1/sensors/today/`;
  handleData(url, showHistory);
};

const loadHistoryAll = function () {
  const url = `http://192.168.168.169:5000/api/v1/sensors/`;
  handleData(url, showHistory);
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
    })

    // toggle history showings
    htmlHistoryToday.addEventListener('click', function () {
      console.log('Showing today');
      this.classList.remove('c-btn--unselected')
      this.classList.add('c-btn--selected');
      // other element
      htmlHistoryAll.classList.add('c-btn--unselected');
      htmlHistoryAll.classList.remove('c-btn--selected');
      loadHistoryToday();
    })
    htmlHistoryAll.addEventListener('click', function () {
      console.log('Showing all');
      this.classList.remove('c-btn--unselected');
      this.classList.add('c-btn--selected');
      // other element
      htmlHistoryToday.classList.add('c-btn--unselected');
      htmlHistoryToday.classList.remove('c-btn--selected');
      loadHistoryAll();
    })
};

const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });
};

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  htmlBoxOpen = document.querySelector('.js-boxopen');
  htmlBoxClose = document.querySelector('.js-boxclose');
  htmlHistoryToday = document.querySelector('.js-historytoday');
  htmlHistoryAll = document.querySelector('.js-historyall')
  listenToUI();
  listenToSocket();
  loadHistoryToday();
});

const handleData = function (url, callbackFunctionName, callbackErrorFunctionName = null, method = 'GET', body = null) {
  fetch(url, {
  method: method,
  body: body,
  headers: {
    'content-type': 'application/json'
  },
  })
  .then(function(response) {
    if (!response.ok) {
      console.warn(`>> Probleem bij de fetch(). Statuscode: ${response.status}`);
      if (callbackErrorFunctionName) {
        console.warn(`>> Callback errorfunctie ${callbackErrorFunctionName.name}(response) wordt opgeroepen`);
        callbackErrorFunctionName(response); 
      } else {
        console.warn('>> Er is geen callback errorfunctie meegegeven als parameter');
      }
    } else {
      console.info('>> Er is een response teruggekomen van de server');
      return response.json();
    }
  })
  .then(function(jsonObject) {
    if (jsonObject) {
      console.info('>> JSONobject is aangemaakt');
      console.info(`>> Callbackfunctie ${callbackFunctionName.name}(response) wordt opgeroepen`);
      callbackFunctionName(jsonObject);
    }
  })
  .catch(function(error) {
    console.warn(`>>fout bij verwerken json: ${error}`);
      if (callbackErrorFunctionName) {
      callbackErrorFunctionName(undefined);
    }
  })
};
