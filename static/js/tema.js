(function () {
  function aplicar(tema) {
    var raiz = document.documentElement;
    if (tema === 'oscuro') {
      raiz.setAttribute('data-tema', 'oscuro');
    } else {
      raiz.removeAttribute('data-tema');
    }
    var boton = document.getElementById('botonTema');
    if (boton) {
      var oscuro = tema === 'oscuro';
      boton.querySelector('span').textContent = oscuro ? 'Modo claro' : 'Modo oscuro';
      boton.querySelector('i').className = oscuro ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }
  }

  function guardado() {
    try { return localStorage.getItem('tema'); } catch (e) { return null; }
  }

  aplicar(guardado());

  document.addEventListener('DOMContentLoaded', function () {
    aplicar(guardado());
    var boton = document.getElementById('botonTema');
    if (!boton) { return; }
    boton.addEventListener('click', function () {
      var actual = document.documentElement.getAttribute('data-tema');
      var nuevo = actual === 'oscuro' ? 'claro' : 'oscuro';
      try { localStorage.setItem('tema', nuevo); } catch (e) {}
      aplicar(nuevo);
      if (document.querySelector('canvas')) { location.reload(); }
    });
  });
})();
// FIN tema.js
