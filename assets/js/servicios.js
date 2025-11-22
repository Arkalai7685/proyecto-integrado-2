// servicios.js
// Maneja el envío del formulario: intenta enviar por AJAX a Django endpoint
// si falla, hace fallback a mailto.

document.addEventListener('DOMContentLoaded', function(){
  function qs(name){
    const params = new URLSearchParams(location.search);
    return params.get(name);
  }

  const serviceEl = document.getElementById('service');
  const planEl = document.getElementById('plan');
  if(serviceEl && qs('service')) serviceEl.value = qs('service');
  if(planEl && qs('plan')) planEl.value = qs('plan');

  const form = document.getElementById('solicitarForm');
  if(!form) return;

  // UI elements for feedback
  let statusBox = document.createElement('div');
  statusBox.className = 'form-status';
  form.parentNode.insertBefore(statusBox, form.nextSibling);

  const submitBtn = form.querySelector('button[type="submit"]');

  // Obtener token CSRF de Django
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrfToken = getCookie('csrftoken');

  form.addEventListener('submit', async function(e){
    e.preventDefault();

    const data = {
      service: document.getElementById('service').value,
      plan: document.getElementById('plan').value,
      name: document.getElementById('name').value,
      email: document.getElementById('email').value,
      phone: document.getElementById('phone').value || '',
      message: document.getElementById('message').value || ''
    };

    // Simple validation
    if(!data.name || !data.email){
      alert('Por favor completa nombre y email.');
      return;
    }

    try{
      // Mostrar loader
      if(submitBtn) { submitBtn.disabled = true; submitBtn.dataset.orig = submitBtn.innerHTML; submitBtn.innerHTML = 'Enviando...'; }
      statusBox.innerText = '';

      const headers = { 
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      };

      const resp = await fetch('/api/submit-order/', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(data)
      });

      const json = await resp.json().catch(()=> null);
      if(resp.ok && json && json.success){
        statusBox.className = 'form-status success';
        statusBox.innerText = 'Solicitud enviada correctamente. Nos contactaremos pronto.';
        form.reset();
      } else {
        const msg = (json && json.message) ? json.message : 'Error al enviar la solicitud';
        statusBox.className = 'form-status error';
        statusBox.innerText = msg;
        throw new Error(msg);
      }
    }catch(err){
      // Fallback: abrir mailto
      console.warn('AJAX failed, falling back to mailto:', err);
      const recipient = 'ventas@impulsamente.example';
      const subject = encodeURIComponent('Solicitud de servicio: ' + data.service + ' - ' + data.plan);
      const body = encodeURIComponent('Nombre: ' + data.name + '\nEmail: ' + data.email + '\nTeléfono: ' + data.phone + '\nServicio: ' + data.service + '\nPlan: ' + data.plan + '\nMensaje: ' + data.message);
      window.location.href = `mailto:${recipient}?subject=${subject}&body=${body}`;
    } finally {
      if(submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = submitBtn.dataset.orig || 'Enviar solicitud'; }
    }
  });
});

