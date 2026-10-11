/* Componentes de interfaz sin dependencias (sistema de diseño: "Ventanas modales").
   UI.confirmar({titulo, texto, aceptar, cancelar, peligro}) -> Promise<boolean>
   UI.notificar(texto, {tipo, titulo, segundos}) -> notificación flotante (info|exito|advertencia|error)
   UI.abrirModal(id) / UI.cerrarModal(id)
   Marcado declarativo:
     <form data-confirmar="¿Eliminar?" data-confirmar-texto="..." data-confirmar-boton="Sí, eliminar">
       pide confirmación con ventana modal antes de enviar (reemplaza a confirm()).
     <button data-abrir-modal="id">  abre <div class="capa" id="id" hidden>
     <button data-cerrar-modal>      cierra la ventana que lo contiene
   Se cierra con Cancelar, con Esc o tocando fuera. */
(function () {
  var ENFOCABLES = 'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  var ultimoFoco = null;

  function escapar(t) {
    var d = document.createElement('div');
    d.textContent = t == null ? '' : String(t);
    return d.innerHTML;
  }

  function buscarCapa(id) {
    return typeof id === 'string' ? document.getElementById(id) : id;
  }

  function abrirModal(id) {
    var capa = buscarCapa(id);
    if (!capa) { return; }
    ultimoFoco = document.activeElement;
    capa.hidden = false;
    document.body.classList.add('con-modal');
    var foco = capa.querySelector('[autofocus], [data-foco-inicial], ' + ENFOCABLES);
    if (foco) { foco.focus(); }
  }

  function cerrarModal(id) {
    var capa = buscarCapa(id);
    if (!capa || capa.hidden) { return; }
    capa.hidden = true;
    if (!document.querySelector('.capa:not([hidden])')) { document.body.classList.remove('con-modal'); }
    capa.dispatchEvent(new CustomEvent('modal-cerrado'));
    if (ultimoFoco && ultimoFoco.focus) { ultimoFoco.focus(); }
  }

  function confirmar(opciones) {
    opciones = opciones || {};
    var peligro = opciones.peligro !== false;
    return new Promise(function (resolver) {
      var capa = document.createElement('div');
      capa.className = 'capa';
      capa.setAttribute('role', 'presentation');
      capa.innerHTML =
        '<div class="modal' + (peligro ? ' peligro' : '') + '" role="alertdialog" aria-modal="true" aria-labelledby="confirmar-titulo" aria-describedby="confirmar-texto">' +
        '<div class="modal-icono" aria-hidden="true"><i class="bi ' + (peligro ? 'bi-exclamation-triangle-fill' : 'bi-question-circle-fill') + '"></i></div>' +
        '<h2 id="confirmar-titulo">' + escapar(opciones.titulo || '¿Estás seguro?') + '</h2>' +
        '<p id="confirmar-texto">' + escapar(opciones.texto || '') + '</p>' +
        '<div class="modal-acciones">' +
        // Foco inicial en Cancelar: Enter por error no borra nada.
        '<button type="button" class="btn btn-borde" data-respuesta="no" data-foco-inicial>' + escapar(opciones.cancelar || 'Cancelar') + '</button>' +
        '<button type="button" class="btn' + (peligro ? ' btn-peligro' : '') + '" data-respuesta="si">' + escapar(opciones.aceptar || 'Aceptar') + '</button>' +
        '</div></div>';
      capa.hidden = true;
      document.body.appendChild(capa);

      var listo = false;
      function terminar(valor) {
        if (listo) { return; }
        listo = true;
        cerrarModal(capa);
        capa.remove();
        resolver(valor);
      }
      capa.addEventListener('click', function (e) {
        var b = e.target.closest('[data-respuesta]');
        if (b) { terminar(b.dataset.respuesta === 'si'); }
      });
      capa.addEventListener('modal-cerrado', function () { terminar(false); });
      abrirModal(capa);
    });
  }

  /* ---------- Teclado: Esc cierra, Tab queda dentro de la ventana ---------- */
  document.addEventListener('keydown', function (e) {
    var abiertas = document.querySelectorAll('.capa:not([hidden])');
    if (!abiertas.length) { return; }
    var capa = abiertas[abiertas.length - 1];
    if (e.key === 'Escape') {
      e.preventDefault();
      cerrarModal(capa);
      return;
    }
    if (e.key === 'Tab') {
      var items = capa.querySelectorAll(ENFOCABLES);
      if (!items.length) { return; }
      var primero = items[0], ultimo = items[items.length - 1];
      if (e.shiftKey && document.activeElement === primero) { e.preventDefault(); ultimo.focus(); }
      else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primero.focus(); }
      else if (!capa.contains(document.activeElement)) { e.preventDefault(); primero.focus(); }
    }
  });

  /* ---------- Clics: abrir, cerrar y tocar fuera ---------- */
  document.addEventListener('click', function (e) {
    var abrir = e.target.closest('[data-abrir-modal]');
    if (abrir) { abrirModal(abrir.dataset.abrirModal); return; }

    var cerrar = e.target.closest('[data-cerrar-modal]');
    if (cerrar) { cerrarModal(cerrar.closest('.capa')); return; }

    if (e.target.classList && e.target.classList.contains('capa') && !e.target.hasAttribute('data-fija')) {
      cerrarModal(e.target);
    }
  });

  /* ---------- Formularios con confirmación ---------- */
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form.dataset.confirmar || form.dataset.confirmado) { return; }
    e.preventDefault();
    confirmar({
      titulo: form.dataset.confirmar,
      texto: form.dataset.confirmarTexto || 'Esta acción no se puede deshacer.',
      aceptar: form.dataset.confirmarBoton || 'Sí, eliminar',
      peligro: form.dataset.confirmarPeligro !== 'no'
    }).then(function (ok) {
      if (ok) {
        // submit() no dispara el evento submit; igual se limpia la marca para que,
        // al volver con "atrás" (bfcache), el formulario vuelva a pedir confirmación.
        form.dataset.confirmado = '1';
        form.submit();
        delete form.dataset.confirmado;
      }
    });
  });

  /* ---------- Notificaciones flotantes (avisos) ---------- */
  var ICONOS = {
    info: 'bi-info-circle-fill',
    exito: 'bi-check-circle-fill',
    advertencia: 'bi-exclamation-triangle-fill',
    error: 'bi-x-circle-fill'
  };
  var SEGUNDOS_POR_DEFECTO = 5;

  function contenedorToasts() {
    var c = document.getElementById('toasts');
    if (!c) {
      c = document.createElement('div');
      c.className = 'toasts';
      c.id = 'toasts';
      document.body.appendChild(c);
    }
    return c;
  }

  /* Da vida a una notificación ya pintada: cierre con la X y temporizador.
     El tiempo lo lleva un setTimeout (no animationend) para que funcione aun con
     "reducir movimiento"; se pausa con el mouse encima o con el foco adentro. */
  function activarToast(t, segundos) {
    var cerrado = false;
    var temporizador = null;
    var restante = segundos * 1000;
    var inicio = 0;

    function cerrar() {
      if (cerrado) { return; }
      cerrado = true;
      clearTimeout(temporizador);
      t.classList.add('saliendo');
      setTimeout(function () { t.remove(); }, 200);
    }
    function correr() {
      // Un solo temporizador a la vez; sigue en pausa mientras haya mouse o foco adentro.
      if (cerrado || temporizador || t.matches(':hover, :focus-within')) { return; }
      inicio = Date.now();
      temporizador = setTimeout(cerrar, Math.max(restante, 0));
    }
    function pausar() {
      if (!temporizador) { return; }
      clearTimeout(temporizador);
      temporizador = null;
      restante -= Date.now() - inicio;
    }

    var boton = t.querySelector('.cerrar');
    if (boton) { boton.addEventListener('click', cerrar); }

    if (segundos > 0) {
      var barra = document.createElement('span');
      barra.className = 'toast-tiempo';
      barra.setAttribute('aria-hidden', 'true');
      barra.style.animationDuration = segundos + 's';
      t.appendChild(barra);
      t.addEventListener('mouseenter', pausar);
      t.addEventListener('focusin', pausar);
      // Al salir, :hover/:focus-within todavía no se actualizaron: reintentar en el próximo tick.
      t.addEventListener('mouseleave', function () { setTimeout(correr, 0); });
      t.addEventListener('focusout', function () { setTimeout(correr, 0); });
      correr();
    }
    return cerrar;
  }

  function leerSegundos(valor) {
    var n = parseFloat(valor);
    return isNaN(n) || n < 0 ? SEGUNDOS_POR_DEFECTO : n;
  }

  /* UI.notificar(texto, {tipo, titulo, segundos}) -> función para cerrarla */
  function notificar(texto, opciones) {
    opciones = opciones || {};
    var tipo = ICONOS[opciones.tipo] ? opciones.tipo : 'info';
    var segundos = opciones.segundos == null
      ? leerSegundos(contenedorToasts().dataset.segundos)
      : leerSegundos(opciones.segundos);
    var t = document.createElement('div');
    t.className = 'toast toast-' + tipo;
    t.setAttribute('role', tipo === 'error' ? 'alert' : 'status');
    t.innerHTML =
      '<i class="bi ' + ICONOS[tipo] + '" aria-hidden="true"></i>' +
      '<div class="toast-texto">' + (opciones.titulo ? '<strong>' + escapar(opciones.titulo) + '</strong>' : '') +
      escapar(texto) + '</div>' +
      '<button type="button" class="cerrar" aria-label="Cerrar aviso"><i class="bi bi-x-lg" aria-hidden="true"></i></button>';
    contenedorToasts().appendChild(t);
    return activarToast(t, segundos);
  }

  /* Avisos que vienen del servidor (?aviso=...): se activan y se limpia la URL
     para que al recargar la página no vuelvan a aparecer. */
  function iniciarAvisos() {
    var avisos = document.querySelectorAll('#toasts .toast[data-segundos]');
    avisos.forEach(function (t) {
      activarToast(t, leerSegundos(t.dataset.segundos));
      // Ya venía en el HTML: se re-escribe el texto para que el lector de pantalla lo anuncie.
      var texto = t.querySelector('.toast-texto');
      if (texto) {
        var contenido = texto.innerHTML;
        texto.innerHTML = '';
        setTimeout(function () { texto.innerHTML = contenido; }, 50);
      }
    });
    if (avisos.length && window.history && history.replaceState) {
      var url = new URL(window.location.href);
      if (url.searchParams.has('aviso')) {
        url.searchParams.delete('aviso');
        history.replaceState(history.state, '', url.pathname + url.search + url.hash);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciarAvisos);
  } else {
    iniciarAvisos();
  }

  window.UI = {
    notificar: notificar,
    confirmar: confirmar,
    abrirModal: abrirModal,
    cerrarModal: cerrarModal
  };
})();
// FIN static/js/ui.js
