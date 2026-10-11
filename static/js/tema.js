(function () {
  function aplicar(tema) {
    var raiz = document.documentElement;
    if (tema === 'oscuro') {
      raiz.setAttribute('data-tema', 'oscuro');
    } else {
      raiz.removeAttribute('data-tema');
    }
    var oscuro = tema === 'oscuro';
    document.querySelectorAll('[data-tema-toggle]').forEach(function (boton) {
      var texto = boton.querySelector('span');
      var icono = boton.querySelector('i');
      if (texto) { texto.textContent = oscuro ? 'Modo claro' : 'Modo oscuro'; }
      if (icono) { icono.className = oscuro ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill'; }
      boton.setAttribute('aria-label', oscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
    });
  }

  function guardado() {
    try { return localStorage.getItem('tema'); } catch (e) { return null; }
  }

  aplicar(guardado());

  document.addEventListener('DOMContentLoaded', function () {
    aplicar(guardado());
    document.querySelectorAll('[data-tema-toggle]').forEach(function (boton) {
      boton.addEventListener('click', function () {
        var actual = document.documentElement.getAttribute('data-tema');
        var nuevo = actual === 'oscuro' ? 'claro' : 'oscuro';
        try { localStorage.setItem('tema', nuevo); } catch (e) {}
        aplicar(nuevo);
        if (document.querySelector('canvas')) { location.reload(); }
      });
    });
  });
})();
// FIN tema.js
