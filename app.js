// app.js — Frontend-only demo for DroneTech Vision Hub
// Uses TensorFlow.js models loaded dynamically. No backend.

const state = {
  mode: 'object', // object | face | pose
  stream: null,
  models: {},
  running: false,
  mirror: false,
};

// UI refs
const loginScreen = document.getElementById('loginScreen');
const dashboard = document.getElementById('dashboard');
const loginForm = document.getElementById('loginForm');
const displayName = document.getElementById('displayName');
const menuBtns = document.querySelectorAll('.menu-btn');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const video = document.getElementById('video');
const overlay = document.getElementById('overlay');
const statusEl = document.getElementById('status');
const modelInfo = document.getElementById('modelInfo');
const flipCam = document.getElementById('flipCam');
const logoutBtn = document.getElementById('logoutBtn');
const userBubble = document.getElementById('userBubble');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

function setStatus(text){ statusEl.textContent = 'Status: ' + text }
function setModel(text){ modelInfo.textContent = 'Model: ' + text }

loginForm.addEventListener('submit', e => {
  e.preventDefault();
  const name = document.getElementById('username').value || 'Pilot';
  displayName.textContent = name;
  // set user bubble initials and tooltip
  if(userBubble){
    // Simple app.js: login/logout only

    const loginScreen = document.getElementById('loginScreen');
    const dashboard = document.getElementById('dashboard');
    const loginForm = document.getElementById('loginForm');
    const clearBtn = document.getElementById('clearBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const logoutBtnFooter = document.getElementById('logoutBtnFooter');
    const userBubble = document.getElementById('userBubble');
    const displayName = document.getElementById('displayName');
    const welcomeName = document.getElementById('welcomeName');

    function showDashboard(name){
      loginScreen.classList.add('hidden');
      dashboard.classList.remove('hidden');
      const initials = name.split(' ').map(s=>s[0]).slice(0,2).join('').toUpperCase();
      if(userBubble) userBubble.querySelector('.initials').textContent = initials;
      if(displayName) displayName.textContent = name;
      if(welcomeName) welcomeName.textContent = name;
      // show logout button in header
      const headerLogout = document.getElementById('logoutBtn');
      if(headerLogout) headerLogout.classList.remove('hidden');
    }

    function showLogin(){
      loginScreen.classList.remove('hidden');
      dashboard.classList.add('hidden');
      const headerLogout = document.getElementById('logoutBtn');
      if(headerLogout) headerLogout.classList.add('hidden');
    }

    loginForm.addEventListener('submit', e=>{
      e.preventDefault();
      const name = document.getElementById('username').value || 'Pilot';
      showDashboard(name);
    });

    clearBtn && clearBtn.addEventListener('click', ()=>{
      document.getElementById('username').value = '';
      document.getElementById('password').value = '';
    });

    logoutBtn && logoutBtn.addEventListener('click', showLogin);
    logoutBtnFooter && logoutBtnFooter.addEventListener('click', showLogin);

    // initial state
    showLogin();
startBtn.addEventListener('click', startStream);

