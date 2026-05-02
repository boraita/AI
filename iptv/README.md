# IPTV España — lista personalizada

Lista M3U con canales públicos españoles para usar en Stremio (vía addon IPTV M3U) o cualquier reproductor compatible (VLC, Kodi, etc.).

## URL para Stremio / VLC

```
https://raw.githubusercontent.com/boraita/AI/main/iptv/spain.m3u
```

## Canales incluidos

| Canal | Fuente |
|-------|--------|
| La 1 | RTVE (oficial) |
| La 2 | RTVE (oficial) |
| Canal Sur | RTVA (oficial) |
| Canal Extremadura | CEXMA (oficial) |

## Cómo usar en Stremio

1. Ir a https://stiptv.ddns.me/ (instancia pública del addon `M3U-XCAPI-EPG-IPTV-Stremio`)
2. Modo: **Direct M3U**
3. M3U URL: pegar la URL de arriba
4. Generar manifest e instalar en Stremio

## Por qué no están Antena 3, Cuatro, Telecinco, La Sexta

Los grupos privados (Atresmedia y Mediaset) protegen sus streams oficiales con tokens dinámicos generados por sus webs (Atresplayer.com, Mitele.es). No es posible incluirlos en una lista M3U estática que funcione de forma duradera. Para verlos hay que usar:

- **Atresplayer.com** (Antena 3, La Sexta) — gratis con cuenta
- **Mitele.es** (Cuatro, Telecinco) — gratis con cuenta
