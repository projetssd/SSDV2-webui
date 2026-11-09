# Développement isolé sur dev

Les changements du catalogue SSDV2 et du parcours QR WireGuard vivent sur les branches
`dev` des dépôts `projetssd/ssdv2` et `projetssd/SSDV2-webui`.

| Copie | Branche | Utilisation |
|---|---|---|
| `/home/kesurof/seedbox-compose` | `master` | Référence principale conservée |
| `/home/kesurof/seedbox-compose-dev` | `dev` | Corrections SSDV2 et tests |
| `/home/kesurof/projets/SSDV2-webui` | `main` | Référence principale conservée |
| `/home/kesurof/projets/SSDV2-webui-dev` | `dev` | WebUI et tests |

Les références principales restent aux SHA `801f229c372cb8d6a84afabbf5170ecf51674205`
(SSDV2) et `99c2b0dd875ca145d3b91ced059dff2c7daf41cd` (WebUI) lors de cette isolation.
Le lot inclut les changements locaux préexistants de SSDV2 Relay, sans les perdre.
Les bases, secrets et données d'exécution ne sont pas copiés dans les worktrees.

## Tests et synchronisation

Utiliser `backend/.venv` et `frontend/node_modules` de la copie WebUI dev. Une
installation Python éditable doit viser ce worktree, jamais le backend principal.
Depuis la racine WebUI dev :

```bash
SSDV2_REPO=/home/kesurof/seedbox-compose-dev bash scripts/sync-ssdv2ctl.sh
python3 scripts/tests/test_image_tags.py
```

Les tests SSDV2 utilisent leurs dossiers temporaires ; `ANSIBLE_PLAYBOOK` permet
de sélectionner explicitement le binaire Ansible du worktree dev. Ne pas changer
`~/.config/ssd/env` ni la configuration des conteneurs installés pour ces tests.

## Publication de la WebUI

Après réussite des contrôles, le workflow de cette branche applique :

| Référence | Événement | Publication |
|---|---|---|
| `dev` | push ou lancement manuel | `ghcr.io/projetssd/ssdv2-webui:dev` uniquement |
| `main` | push ou lancement manuel | `:latest` uniquement |
| tag `v*` valide pour Docker | push ou lancement manuel | tag de version uniquement |
| PR ou autre branche | tous | construction sans publication |

La politique est testée par `scripts/tests/test_image_tags.py` et les tags sont
déduits de la référence Git, sans saisie libre. La publication reste multiarchitecture
amd64/arm64. Un push `dev` ne crée ni ne modifie `latest`.

Cette politique est portée par `dev` : le workflow existant de `main` est inchangé
tant qu'aucune fusion n'a été demandée. Le pousser ou le lancer n'entre pas dans ce lot.
Aucune mise à jour du conteneur installé n'est déclenchée par la publication de `:dev`.
