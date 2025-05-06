// static/share_modal.js
;(function(){
  // 1. 找到 Modal 元素并实例化
  const shareModalEl = document.getElementById('shareModal');
  if (!shareModalEl) return;
  const shareModal = new bootstrap.Modal(shareModalEl);

  // 2. 触发按钮：侧边栏那个 link
  const trigger = document.querySelector('a[data-bs-target="#shareModal"]');
  if (trigger) {
    trigger.addEventListener('click', function(e){
      e.preventDefault();
      // 每次打开前清空搜索框和结果
      const input = document.getElementById('friendSearchInput');
      const list  = document.getElementById('friendListContainerGlobal');
      if (input) input.value = '';
      if (list)  list.innerHTML = '';
      shareModal.show();
    });
  }

  // 3. 搜索相关元素
  const input         = document.getElementById('friendSearchInput');
  const btn           = document.getElementById('friendSearchBtn');
  const listContainer = document.getElementById('friendListContainerGlobal');
  // 这里的 URL 要跟你的 Flask 路由保持一致
  const baseUrl       = window.SHARE_MODAL_BASE_URL;

  if (!input || !btn || !listContainer || !baseUrl) {
    console.error('Share modal: missing elements or baseUrl');
    return;
  }

  // 4. 渲染函数
  function renderFriends(users) {
    if (!users.length) {
      listContainer.innerHTML = `<p class="text-muted">
        No matching friends for “${input.value.trim()}”
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

  // 5. 点击搜索
  btn.addEventListener('click', async function(){
    const q = input.value.trim();
    if (!q) {
      listContainer.innerHTML = '';
      return;
    }
    try {
      const resp = await fetch(`${baseUrl}?search=${encodeURIComponent(q)}`, {
        headers: { 'Accept': 'application/json' }
      });
      if (!resp.ok) throw new Error(resp.status);
      const users = await resp.json();
      renderFriends(users);
    } catch (err) {
      console.error('Share modal search error', err);
    }
  });

  // 6. 回车触发搜索
  input.addEventListener('keydown', function(e){
    if (e.key === 'Enter') {
      e.preventDefault();
      btn.click();
    }
  });
})();
