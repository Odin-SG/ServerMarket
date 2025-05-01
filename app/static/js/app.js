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
        const body = document.getElementById('modalBody');
        body.innerHTML = `
          <div class="row">
            <div class="col-md-6">
              ${
                data.image_url
                  ? `<img src="${data.image_url}" class="img-fluid" alt="${data.model_name}">`
                  : ''
              }
            </div>
            <div class="col-md-6">
              <p>${
                data.specifications
                  ? Object.entries(data.specifications)
                      .map(([k, v]) => `<strong>${k}:</strong> ${v}<br>`)
                      .join('')
                  : ''
              }</p>
              <p class="fs-4"><strong>Цена:</strong> ${data.price.toFixed(2)} ₽</p>
            </div>
          </div>
        `;
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
});
