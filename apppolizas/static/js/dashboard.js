document.addEventListener('DOMContentLoaded', function() {
    const btnLogout = document.getElementById('btnLogout');

    // 1. Verificar si existe el token (Seguridad básica en cliente)
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login-analista/'; // Redirigir si no hay token
    }

    // 2. Lógica de Cerrar Sesión
    btnLogout.addEventListener('click', function() {
        // Eliminar el token del almacenamiento
        localStorage.removeItem('access_token');
        
        alert('Sesión cerrada correctamente');
        
        // Redirigir al login
        window.location.href = '/login-analista/';
    });
});