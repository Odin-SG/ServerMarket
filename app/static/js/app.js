document.addEventListener('DOMContentLoaded', () => {
  const serverModalEl = document.getElementById('serverModal');
  if (serverModalEl) {
    const serverModal = new bootstrap.Modal(serverModalEl);

    window.loadInfo = async function(slug) {
      try {
        const res = await fetch(`/servers/${slug}/info`);
        if (!res.ok) throw new Error(`Ошибка ${res.status}`);
        const data = await res.json();

        document.getElementById('serverModalLabel').textContent = data.model_name;

        const imgHtml = data.image_filename
          ? `<img src="/static/uploads/${data.image_filename}" class="img-fluid" alt="${data.model_name}">`
          : (data.image_url
              ? `<img src="${data.image_url}" class="img-fluid" alt="${data.model_name}">`
              : '');

        const specsHtml = data.specifications
          ? Object.entries(data.specifications)
              .map(([k, v]) => `<strong>${k}:</strong> ${v}<br>`)
              .join('')
          : '';

        document.getElementById('modalBody').innerHTML = `
          <div class="row">
            <div class="col-md-6">
              ${imgHtml}
            </div>
            <div class="col-md-6">
              <p class="mb-3"><em>${data.description}</em></p>
              <p>${specsHtml}</p>
              <p class="fs-4"><strong>Цена:</strong> ${data.price.toFixed(2)} ₽</p>
              <hr>
              <h5>Статистика продаж</h5>
              <table class="table table-sm">
                <tr><td>Всего продано:</td><td>${data.total_sold}</td></tr>
                <tr><td>Выручка:</td><td>${data.total_revenue.toFixed(2)} ₽</td></tr>
                <tr><td>Заказов:</td><td>${data.orders_count}</td></tr>
              </table>
            </div>
          </div>`;
        serverModal.show();
      } catch (e) {
        console.error(e);
        alert('Не удалось загрузить информацию о сервере.');
      }
    };
  }

  if (typeof CONFIG_SLOTS !== 'undefined') {
    const configSelect = document.getElementById('configuration');
    const itemsContainer = document.getElementById('itemsContainer');
    const itemTemplate = document.getElementById('itemTemplate');

    function rebuildItems() {
      const slots = CONFIG_SLOTS[configSelect.value] || 1;
      itemsContainer.innerHTML = '';
      for (let i = 0; i < slots; i++) {
        const clone = itemTemplate.content.cloneNode(true);
        clone.querySelectorAll('[name]').forEach(el => {
          el.name = el.name.replace('__index__', i);
          el.id   = el.id.replace('__index__', i);
        });
        const legend = clone.querySelector('legend');
        if (legend) legend.textContent = `Позиция ${i + 1}`;
        itemsContainer.appendChild(clone);
      }
    }

    configSelect.addEventListener('change', rebuildItems);
    rebuildItems();
  }

  window.addToCart = async function(serverId) {
    const btn = document.querySelector(`.add-to-cart-btn[data-id="${serverId}"]`);
    const maxQty = parseInt(btn.dataset.max, 10);

    try {
      const res = await fetch("/cart/add", {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({server_id: serverId, quantity: 1})
      });

      if (res.status === 401) {
        window.location = window.LOGIN_URL;
        return;
      }
      const data = await res.json();
      if (!res.ok || !data.success) {
        showToast('Не удалось добавить в корзину', 'danger');
        return;
      }

      document.getElementById('cartCount').textContent = data.cart_count;
      showToast('Добавлено в корзину', 'success');

      if (!isNaN(maxQty) && data.cart_count >= maxQty) {
        btn.disabled = true;
        btn.textContent = 'Нет на складе';
      }

    } catch (e) {
      console.error(e);
      showToast('Ошибка при добавлении в корзину', 'danger');
    }
  };

  function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
    toast.style.zIndex = 1050;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }
});
