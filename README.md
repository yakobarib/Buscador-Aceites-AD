# Buscador de Aceites AD Parts

Aplicación web de archivo único para identificar el aceite de motor recomendado por AD Parts para cualquier vehículo, con equivalencias en Castrol, Repsol, Shell y Eni.

## Archivo activo

`APP/HTML/buscador_aceite_demo_v20.html`

Ábrelo directamente en el navegador. Sin servidor, sin dependencias.

## Estructura del repositorio

```
APP/HTML/
  buscador_aceite_demo_v20.html   ← versión activa
  index.html                       ← redirección opcional

BASE DE CONOCIMIENTO/
  TARIFAS/           ← Excel de referencias y precios por marca (Abril 2026)
  EQUIVALENCIAS/     ← Excel de equivalencias entre marcas (mantenido por Yakoba)
  HOMOLOGACIONES/    ← Excel de homologaciones por fabricante
  CATALOGOS/         ← PDFs de catálogo (solo local, no en git)
  NORMATIVAS/        ← PDFs de normativas ACEA/API/OEM (solo local)

BRANDING/            ← Logos SVG AD Parts y Recambios Ibiza
```

## Búsquedas disponibles

| Pestaña | Uso |
|---|---|
| Matrícula | Matrícula española → vehículo → aceite |
| Bastidor | VIN 17 chars → vehículo exacto → aceite |
| Vehículo | Selección manual marca / modelo / año |
| Búsqueda libre | Norma OEM, referencia de producto, viscosidad, código AD |

## Créditos

Crafted by **Yakoba Moreno** · Coded in **Claude Code** (Anthropic)
