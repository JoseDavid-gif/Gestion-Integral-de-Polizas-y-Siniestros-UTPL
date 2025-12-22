document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const errorDiv = document.getElementById('errorMessage');

    form.addEventListener('submit', function(e) {
        e.preventDefault(); // Evitar el submit tradicional

        // Obtener datos
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Limpiar errores previos
        errorDiv.textContent = '';

        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // GUARDAR JWT
                // Opción A: LocalStorage (Persistente)
                localStorage.setItem('access_token', data.token);

                window.location.href = '/dashboard-analista/';
                
                // Opción B: SessionStorage (Se borra al cerrar pestaña)
                // sessionStorage.setItem('access_token', data.token);

                alert('Login correcto. Token guardado.');
                
                // Redirigir al dashboard (ajusta la URL según tu proyecto)
                window.location.href = '/dashboard-analista/'; 
            } else {
                errorDiv.textContent = data.error || 'Error desconocido';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            errorDiv.textContent = 'Ocurrió un error en la conexión.';
        });
    });
});