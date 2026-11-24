// Cookie consent
(function() {
  const consent = localStorage.getItem('cookie_consent');
  const banner = document.getElementById('cookie-banner');
  if (!consent && banner) banner.classList.remove('hidden');
  const accept = document.getElementById('cookie-accept');
  const decline = document.getElementById('cookie-decline');
  if (accept) accept.addEventListener('click', () => { localStorage.setItem('cookie_consent','accepted'); if (banner) banner.classList.add('hidden'); });
  if (decline) decline.addEventListener('click', () => { localStorage.setItem('cookie_consent','declined'); if (banner) banner.classList.add('hidden'); });
})();

// Auto-update check (website version)
(function() {
  const CURRENT_VERSION = '2.1.0';
  const stored = localStorage.getItem('playtree_web_version');
  if (stored && stored !== CURRENT_VERSION) console.log('PLAYTREE website updated to v' + CURRENT_VERSION);
  localStorage.setItem('playtree_web_version', CURRENT_VERSION);
})();

// PWA install prompt
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const banner = document.getElementById('install-banner');
  if (banner) banner.classList.remove('hidden');
});

const SFX = {
  ctx: null,
  init() { if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)(); },
  play(type) {
    try {
      this.init();
      const c = this.ctx, t = c.currentTime;
      const o = c.createOscillator(), g = c.createGain();
      o.connect(g); g.connect(c.destination);
      switch (type) {
        case 'click':
          o.type='sine'; o.frequency.setValueAtTime(600,t); o.frequency.exponentialRampToValueAtTime(400,t+.1);
          g.gain.setValueAtTime(.12,t); g.gain.exponentialRampToValueAtTime(.001,t+.1); o.start(t); o.stop(t+.1); break;
        case 'hover':
          o.type='sine'; o.frequency.setValueAtTime(800,t); g.gain.setValueAtTime(.04,t); g.gain.exponentialRampToValueAtTime(.001,t+.06); o.start(t); o.stop(t+.06); break;
        case 'confirm':
        case 'collect':
          o.type='sine'; o.frequency.setValueAtTime(500,t); o.frequency.setValueAtTime(700,t+.1); g.gain.setValueAtTime(.15,t); g.gain.exponentialRampToValueAtTime(.001,t+.25); o.start(t); o.stop(t+.25); break;
        case 'magic':
          o.type='triangle'; o.frequency.setValueAtTime(400,t); o.frequency.exponentialRampToValueAtTime(900,t+.2); g.gain.setValueAtTime(.08,t); g.gain.exponentialRampToValueAtTime(.001,t+.3); o.start(t); o.stop(t+.3); break;
        case 'error':
          o.type='sawtooth'; o.frequency.setValueAtTime(200,t); o.frequency.exponentialRampToValueAtTime(100,t+.2); g.gain.setValueAtTime(.1,t); g.gain.exponentialRampToValueAtTime(.001,t+.25); o.start(t); o.stop(t+.25); break;
        default:
          o.type='sine'; o.frequency.setValueAtTime(500,t); g.gain.setValueAtTime(.05,t); g.gain.exponentialRampToValueAtTime(.001,t+.08); o.start(t); o.stop(t+.08);
      }
    } catch (_) {}
  }
};

// Shared account helpers
const Account = {
  users() { try { return JSON.parse(localStorage.getItem('gostudios_users') || localStorage.getItem('rhystech_users') || '{}'); } catch { return {}; } },
  save(u) { localStorage.setItem('gostudios_users', JSON.stringify(u)); },
  session() { try { return JSON.parse(localStorage.getItem('gostudios_session') || localStorage.getItem('rhystech_session') || 'null'); } catch { return null; } },
  setSession(s) { if (s) localStorage.setItem('gostudios_session', JSON.stringify(s)); else { localStorage.removeItem('gostudios_session'); localStorage.removeItem('rhystech_session'); } }
};

function initParticles() {
  const root = document.getElementById('particles-bg');
  if (!root) return;
  const c = document.createElement('canvas');
  c.style.width='100%'; c.style.height='100%';
  root.appendChild(c);
  const ctx = c.getContext('2d');
  let w,h,pts;
  function resize() {
    w=c.width=window.innerWidth; h=c.height=window.innerHeight;
    pts=Array.from({length:Math.min(80,Math.floor(w*h/18000))},()=>({x:Math.random()*w,y:Math.random()*h,r:Math.random()*2+.5,vx:(Math.random()-.5)*.3,vy:-Math.random()*.4-.1,a:Math.random()*.5+.2}));
  }
  function draw() {
    ctx.clearRect(0,0,w,h);
    for(const p of pts){p.x+=p.vx;p.y+=p.vy;if(p.y<-10){p.y=h+10;p.x=Math.random()*w;}if(p.x<-10)p.x=w+10;if(p.x>w+10)p.x=-10;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle=`rgba(80,255,120,${p.a})`;ctx.fill();}
    requestAnimationFrame(draw);
  }
  window.addEventListener('resize',resize); resize(); draw();
}

function initNav() {
  const nav=document.getElementById('navbar');
  if(nav){const onScroll=()=>nav.classList.toggle('scrolled',window.scrollY>20);window.addEventListener('scroll',onScroll,{passive:true});onScroll();}
  const menuButton=document.getElementById('menu-button');
  const navLinks=document.getElementById('nav-links');
  if(menuButton&&navLinks){
    menuButton.addEventListener('click',()=>{const open=navLinks.classList.toggle('open');menuButton.setAttribute('aria-expanded',open?'true':'false');});
    navLinks.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{navLinks.classList.remove('open');menuButton.setAttribute('aria-expanded','false');}));
  }
}

function initCounters() {
  const nums=document.querySelectorAll('.stat-num[data-count]');
  if(!nums.length)return;
  const obs=new IntersectionObserver(entries=>{for(const e of entries){if(!e.isIntersecting)continue;const el=e.target;const target=parseInt(el.dataset.count,10)||0;let cur=0;const step=Math.max(1,Math.ceil(target/40));const timer=setInterval(()=>{cur=Math.min(target,cur+step);el.textContent=String(cur);if(cur>=target)clearInterval(timer);},30);obs.unobserve(el);}},{threshold:.4});
  nums.forEach(n=>obs.observe(n));
}

function initReveal() {
  const items=document.querySelectorAll('.feature-card,.timeline-item,.download-card');
  items.forEach(i=>i.classList.add('reveal'));
  const obs=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){e.target.classList.add('visible');obs.unobserve(e.target);}},{threshold:.15});
  items.forEach(i=>obs.observe(i));
}

function initAuth() {
  const modal=document.getElementById('auth-modal');
  const authBtn=document.getElementById('auth-btn');
  if(!modal||!authBtn)return;
  const signupBtn=document.getElementById('signup-btn');
  const closeBtn=modal.querySelector('.modal-close');
  const overlay=modal.querySelector('.modal-overlay');
  const loginPanel=document.getElementById('auth-login');
  const regPanel=document.getElementById('auth-register');
  const profilePanel=document.getElementById('auth-profile');
  const msg=document.getElementById('auth-message');
  function showMsg(text,ok){if(!msg)return;msg.textContent=text;msg.className='auth-msg '+(ok?'ok':'err');msg.classList.remove('hidden');setTimeout(()=>msg.classList.add('hidden'),3000);}
  function showPanel(name){
    [loginPanel,regPanel,profilePanel].forEach(p=>p&&p.classList.add('hidden'));
    if(name==='login'&&loginPanel)loginPanel.classList.remove('hidden');
    if(name==='register'&&regPanel)regPanel.classList.remove('hidden');
    if(name==='profile'&&profilePanel)profilePanel.classList.remove('hidden');
  }
  function showProfile(session){
    showPanel('profile');
    const u=Account.users()[session.email]||{name:session.name||'Player',email:session.email,since:session.since||new Date().getFullYear()};
    const set=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v;};
    set('profile-name',u.name||'Player');set('profile-email',u.email||'');set('profile-since',u.since||new Date().getFullYear());
    set('profile-hours',u.hours||0);set('profile-rounds',u.rounds||0);set('profile-bosses',u.bosses||0);
    const av=document.getElementById('profile-avatar');if(av)av.textContent=(u.name||'P').charAt(0).toUpperCase();
    authBtn.textContent=u.name||'Account';
  }
  function openModal(panel){modal.classList.remove('hidden');const s=Account.session();if(s&&s.email)showProfile(s);else showPanel(panel||'login');}
  function closeModal(){modal.classList.add('hidden');}
  const s=Account.session();if(s&&s.email)authBtn.textContent=s.name||'Account';
  authBtn.addEventListener('click',()=>{SFX.play('click');openModal(Account.session()?'profile':'login');});
  if(signupBtn)signupBtn.addEventListener('click',()=>{SFX.play('click');openModal('register');});
  if(closeBtn)closeBtn.addEventListener('click',closeModal);
  if(overlay)overlay.addEventListener('click',closeModal);
  const showReg=document.getElementById('show-register');
  const showLog=document.getElementById('show-login');
  if(showReg)showReg.addEventListener('click',e=>{e.preventDefault();showPanel('register');});
  if(showLog)showLog.addEventListener('click',e=>{e.preventDefault();showPanel('login');});
  const loginForm=document.getElementById('login-form');
  if(loginForm)loginForm.addEventListener('submit',e=>{
    e.preventDefault();
    const email=(document.getElementById('login-email').value||'').trim().toLowerCase();
    const pass=document.getElementById('login-password').value||'';
    const u=Account.users()[email];
    if(!u||u.password!==pass){SFX.play('error');showMsg('Invalid email or password.',false);return;}
    const sess={email,name:u.name,since:u.since};Account.setSession(sess);SFX.play('confirm');showProfile(sess);showMsg('Signed in.',true);
  });
  const regForm=document.getElementById('register-form');
  if(regForm)regForm.addEventListener('submit',e=>{
    e.preventDefault();
    const name=(document.getElementById('reg-name').value||'').trim();
    const email=(document.getElementById('reg-email').value||'').trim().toLowerCase();
    const pass=document.getElementById('reg-password').value||'';
    const conf=document.getElementById('reg-confirm').value||'';
    if(pass.length<6){SFX.play('error');showMsg('Password must be at least 6 characters.',false);return;}
    if(pass!==conf){SFX.play('error');showMsg('Passwords do not match.',false);return;}
    const users=Account.users();
    if(users[email]){SFX.play('error');showMsg('Account already exists.',false);return;}
    users[email]={name,email,password:pass,since:new Date().getFullYear(),hours:0,rounds:0,bosses:0};Account.save(users);
    const sess={email,name,since:users[email].since};Account.setSession(sess);SFX.play('confirm');showProfile(sess);showMsg('Account created.',true);
  });
  const logout=document.getElementById('logout-btn');
  if(logout)logout.addEventListener('click',()=>{Account.setSession(null);authBtn.textContent='Sign In';showPanel('login');SFX.play('click');showMsg('Signed out.',true);});
}

function initTrailer() {
  const btn=document.getElementById('trailer-btn');
  const modal=document.getElementById('trailer-modal');
  if(!btn||!modal)return;
  const overlay=modal.querySelector('.modal-overlay');
  const close=modal.querySelector('.modal-close');
  function open(){modal.classList.remove('hidden');SFX.play('click');}
  function shut(){modal.classList.add('hidden');}
  btn.addEventListener('click',open);
  if(close)close.addEventListener('click',shut);
  if(overlay)overlay.addEventListener('click',shut);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!modal.classList.contains('hidden'))shut();});
}

function initSfx() {
  document.querySelectorAll('[data-sfx]').forEach(el=>{
    const type=el.getAttribute('data-sfx')||'click';
    if(type==='hover')el.addEventListener('mouseenter',()=>SFX.play('hover'));
    else el.addEventListener('click',()=>SFX.play(type));
  });
}

document.addEventListener('DOMContentLoaded',()=>{
  initParticles(); initNav(); initCounters(); initReveal(); initAuth(); initTrailer(); initSfx();
  const installBtn=document.getElementById('install-btn');
  if(installBtn)installBtn.addEventListener('click',async()=>{
    if(!deferredPrompt)return;
    deferredPrompt.prompt();await deferredPrompt.userChoice;deferredPrompt=null;
    const banner=document.getElementById('install-banner');if(banner)banner.classList.add('hidden');
  });
  const installDismiss=document.getElementById('install-dismiss');
  if(installDismiss)installDismiss.addEventListener('click',()=>{const banner=document.getElementById('install-banner');if(banner)banner.classList.add('hidden');});
});












