[Español](README.es.md) | [English](README.en.md)

---

# pushguard

Comprobaciones de seguridad antes de `git push`. Verifica que tu codigo este seguro y sincronizado antes de empujarlo a repositorios remotos.

## Inicio rapido

```bash
git clone https://github.com/mdwcoder/pushguard.git
cd pushguard
bash init.sh
pushguard --help
```

Si `init.sh` no es ejecutable:

```bash
chmod +x init.sh
./init.sh
```

`init.sh` intenta instalar con `pipx`. Si no esta disponible, crea un virtualenv en `~/.local/pushguard/venv` y enlaza el CLI en `~/.local/bin`.

## Uso basico

```bash
pushguard
```

Ejecuta:

- `fetch` del remoto.
- Comprobacion de sincronizacion.
- Escaneos de seguridad.
- `git push` solo si todo esta correcto.

## Autopull

```bash
pushguard --autopull rebase
pushguard --autopull merge
```

Si aparecen conflictos, pushguard se detiene y muestra instrucciones.

## Seguridad

- Bloquea `.env` rastreados por Git.
- Detecta patrones de secretos.
- Revisa `.gitignore`.
- Evita empujar ramas desactualizadas o divergentes sin resolver.

## Plataformas

Recomendado en Linux y macOS. En Windows, usa Git Bash o WSL.
