---
name: negocio-costos
description: "Trigger: costo, precio, margen, receta, fabricado, compra, venta, pedido, gastos, delivery, unidades, redondeo, ganancia. Reglas de dominio de Mi Negocio."
license: Apache-2.0
metadata:
  author: carlos-capella
  version: "1.0"
---

## Activation Contract

Usar al tocar cálculos de costo/precio/margen/ganancia, unidades, compras, recetas, fabricados, pedidos o sus tests en `services/`, `routes/` o `templates/`.

## Hard Rules

- Dinero y cantidades: `Decimal`; desde DB/float usar `Decimal(str(x))`. Nunca operar floats.
- Input de usuario: `services/numeros.leer_decimal` (formato AR `1.234,50`). Ver gotcha `"1.200"` en referencia.
- Redondeo ROUND_HALF_UP: `precio_unitario` compra 0.0001; totales compra/pedido 0.01; precios finales tienda/delivery con `margenes.redondear(valor, modo)` (`entero` por defecto). Costos NUNCA se redondean.
- Unidades solo vía `unidades.convertir`; incompatibles → `ErrorUnidad`. Sin densidad (g↔ml no).
- Margen = **sobre precio**, no markup: `precio = costo_con_gastos / (1 - m/100)`. `m >= 100` inválido.
- Gastos = % sumados al costo: `costo * (1 + Σgastos/100)`. Delivery = `tienda / (1 - Σdelivery/100)` sobre tienda ya redondeado.
- Precio de insumo = ÚLTIMA compra por fecha (no promedio), por unidad de compra.
- Costos de receta/fabricado se calculan en vivo; no se persisten.
- No existe stock, merma ni IVA real. No inventarlos sin SDD.
- Errores: `Error<Modulo>(ValueError)` con mensaje en español, voseo ("Elegí…", "Agregá…").
- Reusar fórmulas existentes; no duplicar (deuda: `fabricados.calcular_fabricado` ya duplica `margenes.calcular_precio`).

## Decision Gates

| Situación | Acción |
|---|---|
| Nueva fórmula de precio | Extender `margenes.py`, test primero en `tests/test_margenes.py` |
| Costo por unidad de fabricado | `costo_lote / cantidad_fabricada` (no `rendimiento_cantidad`) |
| Cambio que congela costo histórico, stock o IVA | Cambio de dominio → `/sdd-new`, migración `NNN_*.sql` |
| Línea de receta incompatible | Hoy cuenta $0 en silencio; marcar `incompatible`, no ocultar |
| Mostrar dinero en vista | Filtro `moneda` de `app.py` |

## Execution Steps

1. Leer `references/dominio.md` sección relevante.
2. Escribir test con valores concretos (ej: costo 500, margen 30 → 714,29 sin redondeo).
3. Implementar en `services/`, reutilizando helpers.
4. Correr `pytest`.

## Output Contract

Indicar fórmula usada, archivo:función tocado y casos borde probados (0, margen 99/100, unidades incompatibles).

## References

- `references/dominio.md` — entidades, fórmulas, errores y gotchas con archivo:función.
