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

  // Cargar empleados disponibles
  const preferredEmployeeSelect = document.getElementById('preferred_employee');
  if (preferredEmployeeSelect && serviceEl && serviceEl.value) {
    loadAvailableEmployees(serviceEl.value);
  }

  // Configurar fecha mínima en el calendario (hoy)
  const startDateInput = document.getElementById('start_date');
  if (startDateInput) {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const minDate = tomorrow.toISOString().split('T')[0];
    startDateInput.setAttribute('min', minDate);
    startDateInput.value = minDate; // Establecer mañana como valor por defecto
  }

  const form = document.getElementById('orderForm') || document.getElementById('solicitarForm');
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

  // Función para cargar empleados disponibles
  async function loadAvailableEmployees(serviceSlug) {
    try {
      const response = await fetch(`/api/available-employees/?service=${serviceSlug}`);
      const data = await response.json();
      
      if (data.success && data.employees) {
        preferredEmployeeSelect.innerHTML = '<option value="">Selecciona uno (opcional)</option>';
        
        data.employees.forEach(emp => {
          const option = document.createElement('option');
          option.value = emp.id;
          option.textContent = `${emp.name} (${emp.active_clients} clientes activos)`;
          preferredEmployeeSelect.appendChild(option);
        });
      } else {
        preferredEmployeeSelect.innerHTML = '<option value="">No hay profesionales disponibles</option>';
      }
    } catch (error) {
      console.error('Error cargando empleados:', error);
      preferredEmployeeSelect.innerHTML = '<option value="">Error al cargar profesionales</option>';
    }
  }

  // Agregar estilos para checkboxes seleccionados
  const dayCheckboxes = document.querySelectorAll('input[name="preferred_days"]');
  dayCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
      const label = this.closest('label');
      if (this.checked) {
        label.style.background = '#e8f0fe';
        label.style.borderColor = '#667eea';
        label.style.fontWeight = '600';
      } else {
        label.style.background = 'white';
        label.style.borderColor = '#ddd';
        label.style.fontWeight = 'normal';
      }
    });
  });

  form.addEventListener('submit', async function(e){
    e.preventDefault();

    // Recopilar días seleccionados
    const selectedDays = [];
    document.querySelectorAll('input[name="preferred_days"]:checked').forEach(checkbox => {
      selectedDays.push(checkbox.value);
    });

    // Validar que se hayan seleccionado días si el campo existe
    const daysExist = document.querySelector('input[name="preferred_days"]');
    if (daysExist && selectedDays.length === 0) {
      alert('Por favor selecciona al menos un día de la semana para tus sesiones.');
      return;
    }

    const data = {
      service: document.getElementById('service').value,
      plan: document.getElementById('plan').value,
      name: document.getElementById('name').value,
      email: document.getElementById('email').value,
      phone: document.getElementById('phone').value || '',
      message: document.getElementById('message').value || '',
      preferred_employee: preferredEmployeeSelect ? preferredEmployeeSelect.value : null,
      start_date: document.getElementById('start_date') ? document.getElementById('start_date').value : null,
      preferred_days: selectedDays,
      preferred_time: document.getElementById('preferred_time') ? document.getElementById('preferred_time').value : null,
      number_of_sessions: document.getElementById('number_of_sessions') ? document.getElementById('number_of_sessions').value : null
    };

    // Simple validation
    if(!data.name || !data.email){
      alert('Por favor completa nombre y email.');
      return;
    }

    // Validar fecha de inicio si el campo existe
    if (document.getElementById('start_date') && !data.start_date) {
      alert('Por favor selecciona la fecha de inicio de tus sesiones.');
      return;
    }

    // Validar hora si el campo existe
    if (document.getElementById('preferred_time') && !data.preferred_time) {
      alert('Por favor selecciona una hora preferida para tus sesiones.');
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
        statusBox.innerText = json.message || 'Solicitud enviada correctamente. Nos contactaremos pronto.';
        statusBox.style.padding = '15px';
        statusBox.style.borderRadius = '8px';
        statusBox.style.marginTop = '20px';
        statusBox.style.background = '#d4edda';
        statusBox.style.color = '#155724';
        statusBox.style.border = '1px solid #c3e6cb';
        form.reset();
        
        // Resetear estilos de los checkboxes
        dayCheckboxes.forEach(checkbox => {
          const label = checkbox.closest('label');
          label.style.background = 'white';
          label.style.borderColor = '#ddd';
          label.style.fontWeight = 'normal';
        });
      } else {
        const msg = (json && json.message) ? json.message : 'Error al enviar la solicitud';
        statusBox.className = 'form-status error';
        statusBox.innerText = msg;
        statusBox.style.padding = '15px';
        statusBox.style.borderRadius = '8px';
        statusBox.style.marginTop = '20px';
        statusBox.style.background = '#f8d7da';
        statusBox.style.color = '#721c24';
        statusBox.style.border = '1px solid #f5c6cb';
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
