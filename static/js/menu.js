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
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { abrir(false); } });
    window.addEventListener('resize', function () { if (window.innerWidth > 900) { abrir(false); } });
  });
})();
// FIN menu.js
