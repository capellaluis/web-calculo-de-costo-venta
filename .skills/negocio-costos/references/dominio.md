# Dominio — Mi Negocio

Fuente de verdad: `services/*.py` y `database/schema.sql`. Si el código cambia, actualizar esto.

## Entidades (schema.sql)

| Tabla | Rol |
|---|---|
| `unidades` | `tipo` (masa/volumen/conteo/empaque), `factor_base`. Base: g, ml, un |
| `productos` | Insumos. `unidad_compra_id`, `unidad_uso_id`, `precio_actual` (por 1 unidad de compra) |
| `compras` + `detalle_compras` | Factura de proveedor; línea con cantidad, unidad, precio_total, precio_unitario |
| `historial_precios` | 1 fila por línea de compra (`detalle_compra_id` ON DELETE SET NULL) |
| `recetas` + `receta_ingredientes` | `rendimiento_cantidad`, `rendimiento_unidad` (texto libre) |
| `productos_fabricados` + `presentaciones` | `receta_id`, `cantidad_fabricada` por lote; presentación `cantidad_unidades` (x6, x12) |
| `fabricado_gastos` / `fabricado_margenes` / `fabricado_delivery` | Config de precio por fabricado (`elegido=1` = margen activo) |
| `gastos`, `margenes` | Config global (Gas/Agua/Luz 0 %; márgenes 30/50/70) |
| `pedidos` + `pedido_items` | Ventas. canal, estado, forma_pago, descuento, total |
| `configuracion` | clave/valor: `redondeo`, `nombre_negocio`, `logo`, `plantilla_*` (JSON) |

`moneda` y `metodo_precio` se siembran pero ningún código los lee.

## Números (`numeros.py`)

- `_limpiar`: quita `$` y espacios; si hay `,` elimina `.` y cambia `,`→`.`.
- `leer_decimal("1.234,50")` → 1234.50; vacío → 0.
- ⚠️ `leer_decimal("1.200")` → **1.2** (punto sin coma se toma como decimal).
- Basura → `InvalidOperation`/`ValueError` crudo (no `Error<Modulo>`).
- `leer_precio` = igual pero `float` (evitar).

## Unidades (`unidades.py`)

`convertir(cant, desde, hacia) = Decimal(cant) * factor(desde) / factor(hacia)`.
`ErrorUnidad`: tipos distintos; empaque (paq/caja) solo a sí mismo.

## Costos

- `compras._aplicar_lineas`: `precio_unitario = _q(precio_total / convertir(cant, u_linea, u_compra))` (4 dec). `precio_actual` se actualiza solo si la fecha es ≥ última del historial.
- `compras._quitar_efectos` (editar/borrar): recalcula `precio_actual` desde historial (`fecha DESC, id DESC`); sin historial → no lo resetea, lo reporta en `sin_historial`.
- `recetas.costo_linea = convertir(cant, u_ing, u_compra) * precio_actual`.
- `recetas.calcular_receta`: `total = Σ líneas`; incompatibles = 0 + `incompatible=True`; `costo_unidad = total / (rendimiento_cantidad or 1)`.
- `fabricados.calcular_fabricado`: `costo_unidad = costo_lote / cantidad_fabricada`; presentación = `costo_unidad * cantidad_unidades`.
- `costos.ranking_ingredientes`: costo por insumo sobre todas las recetas; `porcentaje` None si total 0.

## Precio y margen (`margenes.py`)

```
con_gastos = costo * (1 + Σgastos/100)        # gastos.monto = costo*pct/100
tienda     = redondear(con_gastos / (1 - m/100))
ganancia   = tienda - con_gastos
delivery   = redondear(tienda / (1 - Σdelivery/100))
```

- `m >= 100`: `calcular_precio`/`calcular_fabricado` devuelven None; validadores lanzan `ErrorMargen`.
- `redondear`: `ninguno` | `entero` (default, `leer_redondeo`) | `centavos`.
- `PLANTILLA_DEFECTO`: gastos 0; márgenes 30 (elegido)/50/70; delivery Comisión 0, IVA 0, 2,9 %.
- Nuevo fabricado se siembra con la última plantilla guardada (`sembrar_config_fabricado`); guardar config sobrescribe plantilla.
- `precios.variacion` → `(diff, diff/anterior*100)`; `aumento = diff > 0`; sin umbral de alerta.

## Ventas (`ventas.py`)

- `CANALES` tienda/delivery; `ESTADOS` nuevo/entregado/cancelado; `FORMAS_PAGO` Efectivo/Transferencia/Tarjeta/Otro.
- `total = max(0, Σ(precio*cant) - descuento)`, `_q` 0.01. Editar reemplaza todos los items.
- Ganancia = `Σ(precio - costo_actual_presentación)*cant - descuento`. Costo NO congelado a la fecha de venta. Items libres → costo 0.
- `resumen_periodo` excluye cancelados.
- No hay stock: ni venta ni fabricación mueven cantidades.

## Errores

`ErrorUnidad`, `ErrorCompra`, `ErrorReceta`, `ErrorMargen`, `ErrorFabricado`, `ErrorVenta`, `ErrorGasto`, `ErrorNegocio` — todos `ValueError`, mensaje en español voseo.

## Gotchas / deuda

1. DB guarda dinero como REAL; `float()` al escribir. `ventas.resumen_periodo` y `leer_pedido` suman floats.
2. `leer_decimal("1.200")` = 1.2.
3. Líneas incompatibles cuentan $0 en silencio.
4. Dos sistemas de margen (global vs por fabricado); fórmula duplicada en `fabricados.calcular_fabricado`.
5. Costo unitario de fabricado ignora `rendimiento_cantidad` de la receta.
6. `guardar_pedido` no valida `estado` (solo `cambiar_estado`).
