// PLAYTREE shared functionality for secondary pages
(function () {
  'use strict';

  const Account = {
    users() { try { return JSON.parse(localStorage.getItem('gostudios_users') || localStorage.getItem('rhystech_users') || '{}'); } catch { return {}; } },
    save(u) { localStorage.setItem('gostudios_users', JSON.stringify(u)); },
    session() { try { return JSON.parse(localStorage.getItem('gostudios_session') || localStorage.getItem('rhystech_session') || 'null'); } catch { return null; } },
    setSession(s) { if (s) localStorage.setItem('gostudios_session', JSON.stringify(s)); else localStorage.removeItem('gostudios_session'); },
    friends() { try { return JSON.parse(localStorage.getItem('playtree_friends') || '[]'); } catch { return []; } },
    saveFriends(f) { localStorage.setItem('playtree_friends', JSON.stringify(f)); }
  };
  window.PTAccount = Account;

  function currentName() {
    const s = Account.session();
    if (s && s.email) {
      const u = Account.users()[s.email];
      return u ? u.name : (s.name || 'Player');
    }
    return 'Player';
  }
  window.PTCurrentName = currentName;

  function showToast(msg) {
    let t = document.getElementById('pt-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'pt-toast';
      t.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:9999;background:rgba(11,25,16,.96);border:1px solid var(--green,#55ef78);color:var(--text,#ecf6ed);padding:12px 20px;border-radius:8px;font-size:.9rem;box-shadow:0 8px 30px rgba(0,0,0,.4)';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    clearTimeout(t._hide);
    t._hide = setTimeout(() => { t.style.display = 'none'; }, 2600);
    t.style.display = 'block';
  }
  window.PTToast = showToast;

  // Update any element that displays the player name
  function applyProfile() {
    const name = currentName();
    document.querySelectorAll('[data-player-name]').forEach(el => el.textContent = name);
    const avatar = document.getElementById('profile-avatar');
    if (avatar) avatar.textContent = (name || 'P').charAt(0).toUpperCase();
    const h1 = document.querySelector('.profile-info h1');
    if (h1) h1.innerHTML = name + ' <span class="badge online">Online</span>';
    const avatars = document.querySelectorAll('.vc-name');
    if (avatars[0]) avatars[0].textContent = 'You (' + name + ')';
    const emailEl = document.getElementById('profile-email');
    const s = Account.session();
    if (emailEl && s && s.email) emailEl.textContent = s.email;
  }
  window.PTApplyProfile = applyProfile;

  // Friends list management
  window.PTFriends = {
    render() {
      const list = document.getElementById('friendsList');
      if (!list) return;
      const friends = Account.friends();
      if (!friends.length) {
        list.innerHTML = '<p class="empty-state">No friends added yet. Use Add Friend to add one.</p>';
        return;
      }
      list.innerHTML = friends.map((f, i) => `
        <div class="friend-item">
          <div class="friend-avatar">${(f.name || '?').charAt(0).toUpperCase()}</div>
          <span class="friend-name">${f.name}</span>
          <span class="friend-status ${f.online ? 'online' : 'offline'}">${f.online ? 'Online' : 'Offline'}</span>
          <button class="friend-remove" onclick="PTFriends.remove(${i})" title="Remove">✕</button>
        </div>`).join('');
    },
    add() {
      const input = document.getElementById('addFriendName');
      const name = input ? (input.value || '').trim() : prompt('Enter friend name:');
      if (!name) return;
      const friends = Account.friends();
      friends.push({ name: name, online: true });
      Account.saveFriends(friends);
      if (input) input.value = '';
      this.render();
      showToast('Added ' + name + ' to friends.');
    },
    remove(i) {
      const friends = Account.friends();
      const removed = friends.splice(i, 1)[0];
      Account.saveFriends(friends);
      this.render();
      showToast('Removed ' + (removed ? removed.name : 'friend') + '.');
    }
  };

  // Login / logout popup for pages that need it
  window.PTLogin = {
    open() {
      const s = Account.session();
      if (s && s.email) {
        if (confirm('Signed in as ' + currentName() + '\n\nSign out?')) {
          Account.setSession(null);
          applyProfile();
          showToast('Signed out.');
        }
        return;
      }
      const email = prompt('Email (GoStudios account):');
      if (!email) return;
      const pass = prompt('Password:');
      if (!pass) return;
      const u = Account.users()[email.trim().toLowerCase()];
      if (!u || u.password !== pass) { showToast('Invalid email or password.'); return; }
      Account.setSession({ email: email.trim().toLowerCase(), name: u.name, since: u.since });
      applyProfile();
      showToast('Signed in as ' + u.name + '.');
    }
  };

  // Install-as-app for minigames
  window.PTInstall = function (name) {
    if (window.deferredPrompt) {
      window.deferredPrompt.prompt();
      window.deferredPrompt.userChoice.then(() => { window.deferredPrompt = null; });
    } else {
      showToast('Install "' + name + '" via your browser menu → Add to Home Screen.');
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    applyProfile();
    PTFriends.render();
    document.querySelectorAll('[data-login-btn]').forEach(b => b.addEventListener('click', () => PTLogin.open()));
  });
})();