; (function () {
  document.addEventListener('DOMContentLoaded', function () {
    console.log('share_modal.js loaded');
    const shareModalEl = document.getElementById('shareModal');
    console.log('modal el:', shareModalEl);

    if (!shareModalEl) return;
    const shareModal = new bootstrap.Modal(shareModalEl);

    const trigger = document.querySelector('a[data-bs-target="#shareModal"]');
    console.log('trigger el:', trigger);
    if (trigger) {
      trigger.addEventListener('click', function (e) {
        e.preventDefault();
        const input = shareModalEl.querySelector('#friendSearchInput');
        const list  = shareModalEl.querySelector('#friendListContainerGlobal');
        if (input) input.value = '';
        if (list)  list.innerHTML = '';
        updateRanges();    
        shareModal.show();
      });
    }

    const formEl         = shareModalEl.querySelector('form');
    const baseUrl        = formEl.getAttribute('action');
    const input          = shareModalEl.querySelector('#friendSearchInput');
    const btn            = shareModalEl.querySelector('#friendSearchBtn');
    const listContainer  = shareModalEl.querySelector('#friendListContainerGlobal');

    if (!formEl || !baseUrl || !input || !btn || !listContainer) {
      console.error('Share modal: missing form/action or elements', {
        formEl, baseUrl, input, btn, listContainer
      });
      return;
    }

    function renderFriends(users, query) {
      if (!users.length) {
        listContainer.innerHTML = `<p class="text-muted">
          No matching friends for “${query}”
        </p>`;
        return;
      }
      listContainer.innerHTML = users.map(u => `
        <label class="list-group-item">
          <input class="form-check-input me-2" type="radio"
                 name="selected_friend_id"
                 value="${u.id}" required>
          ${u.first_name} ${u.last_name} (${u.email})
        </label>
      `).join('');
    }

    async function doSearch() {
      const q = input.value.trim();
      if (!q) {
        listContainer.innerHTML = '';
        return;
      }
      try {
        const url  = `${baseUrl}?search=${encodeURIComponent(q)}`;
        const resp = await fetch(url, {
          headers: { 'Accept': 'application/json' }
        });
        if (!resp.ok) throw new Error(`Status ${resp.status}`);
        const users = await resp.json();
        renderFriends(users, q);
      } catch (err) {
        console.error('Share modal search error', err);
        listContainer.innerHTML = `<p class="text-danger">
          Search failed. See console.
        </p>`;
      }
    }

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      doSearch();
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        doSearch();
      }
    });

    const typeRadios    = shareModalEl.querySelectorAll('input[name="content_type"]');
    const rangeWrappers = shareModalEl.querySelectorAll('[data-range]');

    function updateRanges() {
      const selected = shareModalEl.querySelector('input[name="content_type"]:checked').value;
      rangeWrappers.forEach(w => {
        const r = w.getAttribute('data-range'); // 'day' / 'week' / 'month'
        if (selected === 'nutrition') {
          w.style.display = (r === 'day') ? '' : 'none';
        }
        else if (selected === 'ranking') {
          w.style.display = (r === 'week' || r === 'month') ? '' : 'none';
        }
        else {
          w.style.display = '';
        }
      });
      const checked = shareModalEl.querySelector('input[name="date_range"]:checked');
      if (checked && checked.closest('[data-range]').style.display === 'none') {
        const firstVisible = Array.from(rangeWrappers).find(w => w.style.display !== 'none');
        if (firstVisible) firstVisible.querySelector('input').checked = true;
      }
    }

    typeRadios.forEach(radio => radio.addEventListener('change', updateRanges));
    updateRanges();
  });
})();
