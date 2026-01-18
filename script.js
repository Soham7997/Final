// script.js — login/dashboard interactions for Drone Tech UI
document.addEventListener('DOMContentLoaded', ()=>{
  // elements on index.html
  const logInBtn = document.getElementById('logInBtn');
  const signInBtn = document.getElementById('signInBtn');
  const loginForm = document.getElementById('loginForm');
  const cancelLogin = document.getElementById('cancelLogin');

  if(logInBtn){
    logInBtn.addEventListener('click', ()=>{
      loginForm.classList.remove('hidden');
      loginForm.querySelector('input')?.focus();
    });
  }
  // Sign In opens the same form (signup flow)
  if(signInBtn){
    signInBtn.addEventListener('click', ()=>{
      loginForm.classList.remove('hidden');
      loginForm.querySelector('input')?.focus();
    });
  }
  if(cancelLogin){
    cancelLogin.addEventListener('click', ()=>{
      loginForm.classList.add('hidden');
    });
  }

  loginForm && loginForm.addEventListener('submit', e=>{
    e.preventDefault();
    const name = document.getElementById('name').value || '';
    const email = document.getElementById('email').value || '';
    // store in session for dashboard
    sessionStorage.setItem('dt_name', name);
    sessionStorage.setItem('dt_email', email);
    window.location.href = 'dashboard.html';
  });

  // dashboard logic
  const greet = document.getElementById('greet');
  if(greet){
    const name = sessionStorage.getItem('dt_name') || '';
    const email = sessionStorage.getItem('dt_email') || sessionStorage.getItem('drone_user') || 'user@example.com';
    const displayName = name || email;
    // show name greeting as requested
    greet.textContent = `Welcome, ${displayName} Greetings For the Day!!!`;
    // set header initials
    const headerUser = document.getElementById('headerUser');
    if(headerUser){
      const initials = (name || email).split(' ').map(s=>s[0]||'').slice(0,2).join('').toUpperCase();
      headerUser.textContent = initials;
    }
    // wire module Open buttons
    document.querySelectorAll('[data-action="open"]').forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const mod = btn.dataset.module;
        // open only when enabled
        if(btn.disabled) return;
        // map module key to page
        const mapping = {object: 'object.html', gender: 'gender.html', body: 'http://localhost:8000'};
        const target = mapping[mod] || 'dashboard.html';
        window.location.href = target;
      });
    });
    // subscription buttons
    const notificationBar = document.getElementById('notificationBar');
    function showNotification(message){
      if(!notificationBar) return;
      notificationBar.textContent = message;
      notificationBar.classList.add('show');
      clearTimeout(window._dt_notify_timeout);
      window._dt_notify_timeout = setTimeout(()=>{
        notificationBar.classList.remove('show');
      }, 3500);
    }

    // helper: load subscriptions from sessionStorage
    const SUB_KEY = 'dt_subscriptions_v1';
    function loadSubscriptions(){
      try{const raw = sessionStorage.getItem(SUB_KEY); return raw?JSON.parse(raw):{}}catch(e){return{}}}
    function saveSubscriptions(obj){sessionStorage.setItem(SUB_KEY,JSON.stringify(obj));}

    function updateCardUI(moduleKey, subscribed){
      const card = document.querySelector(`.card[data-module="${moduleKey}"]`);
      if(!card) return;
      const openBtn = card.querySelector('[data-action="open"]');
      const subBtn = card.querySelector('[data-action="subscribe"]');
      if(subscribed){
        card.classList.add('subscribed');
        if(openBtn){openBtn.disabled = false; openBtn.classList.remove('disabled');}
        if(subBtn){subBtn.textContent = 'Unsubscribe'; subBtn.classList.add('primary');}
      } else {
        card.classList.remove('subscribed');
        if(openBtn){openBtn.disabled = true; openBtn.classList.add('disabled');}
        if(subBtn){subBtn.textContent = 'Subscribe'; subBtn.classList.remove('primary');}
      }
    }

    // initialize from storage
    const subs = loadSubscriptions();
    ['object','gender','body'].forEach(k=>{
      updateCardUI(k, !!subs[k]);
    });

    // wire subscribe/unsubscribe
    document.querySelectorAll('[data-action="subscribe"]').forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const mod = btn.dataset.module;
        const current = !!(loadSubscriptions()[mod]);
        const updated = loadSubscriptions();
        if(current){
          delete updated[mod];
          saveSubscriptions(updated);
          updateCardUI(mod, false);
          showNotification(`Unsubscribed from ${btn.closest('.card').querySelector('.module-title').innerText.replace(' ✓','')}`);
        } else {
          updated[mod] = true;
          saveSubscriptions(updated);
          updateCardUI(mod, true);
          showNotification(`Subscribed to ${btn.closest('.card').querySelector('.module-title').innerText.replace(' ✓','')}`);
        }
      });
    });
    // logout
    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn && logoutBtn.addEventListener('click', doLogout);
    const logoutBtnBox = document.getElementById('logoutBtnBox');
    logoutBtnBox && logoutBtnBox.addEventListener('click', doLogout);
    function doLogout(){
      sessionStorage.removeItem('dt_name');
      sessionStorage.removeItem('dt_email');
      window.location.href = 'index.html';
    }
  }
});
