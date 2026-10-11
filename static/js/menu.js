(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var menu = document.getElementById('menuLateral');
    var fondo = document.getElementById('menuFondo');
    var botones = [document.getElementById('botonMenu'), document.getElementById('botonMas')];
    if (!menu || !fondo) { return; }

    function abrir(si) {
      menu.classList.toggle('abierto', si);
      fondo.classList.toggle('abierto', si);
      botones.forEach(function (b) { if (b) { b.setAttribute('aria-expanded', si ? 'true' : 'false'); } });
    }

    botones.forEach(function (b) {
      if (b) { b.addEventListener('click', function () { abrir(!menu.classList.contains('abierto')); }); }
    });
    fondo.addEventListener('click', function () { abrir(false); });
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) { abrir(false); }
    });
    // Acordeón exclusivo: al abrir un grupo se cierran los demás (excepto Sesión).
    var grupos = Array.prototype.slice.call(menu.querySelectorAll('.menu-grupo:not(.menu-sesion .menu-grupo)'));
    grupos.forEach(function (g) {
      g.addEventListener('toggle', function () {
        if (!g.open) { return; }
        grupos.forEach(function (o) { if (o !== g) { o.open = false; } });
      });
    });
    // Estado inicial: solo el grupo de la sección activa (o el primero).
    var activo = menu.querySelector('.menu-grupo .nav-item.activo');
    var inicial = (activo && activo.closest('.menu-grupo')) || grupos[0];
    grupos.forEach(function (g) { g.open = (g === inicial); });

    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { abrir(false); } });
    window.addEventListener('resize', function () { if (window.innerWidth > 900) { abrir(false); } });
  });
})();
// FIN menu.js
