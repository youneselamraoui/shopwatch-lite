import re
from src.contrat import Signal

_SENSITIVE = ['password', 'pwd', 'token', 'secret', 'card', 'iban']

def masquer_donnees(texte: str) -> str:
    if not texte:
        return texte
    pattern = re.compile(r'(?i)\b(' + '|'.join(_SENSITIVE) + r')\s*([=:])\s*([^ \t&;,]+)')
    def repl(m):
        name = m.group(1)
        sep = m.group(2)
        return f'{name}{sep}[MASQUE]'
    return pattern.sub(repl, texte)

def lire_journal(ligne: str, numero: int, origine: str = 'PAIEMENT', env: str = 'production') -> Signal:
    m = re.match(r'^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (\S+) (\S+) (.+)$', ligne)
    if not m:
        parts = ligne.split()
        if len(parts) < 5:
            raise ValueError('Ligne journal invalide: moins de 5 champs')
        raise ValueError('Ligne journal invalide')
    date_part, time_part, service, niveau, message = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
    date_iso = f'{date_part}T{time_part}Z'
    ref = f'SH-{numero:04d}'
    categorie = 'JOURNAL'
    niveau_upper = niveau.upper()
    if niveau_upper in ('FATAL', 'CRITICAL'):
        gravite = 'BLOQUANT'
    elif niveau_upper == 'ERROR':
        gravite = 'MAJEUR'
    elif niveau_upper in ('WARN', 'WARNING'):
        gravite = 'MODERE'
    else:
        gravite = 'MINEUR'
    texte = masquer_donnees(message)
    return Signal(ref=ref, date=date_iso, origine=origine, service=service, env=env, categorie=categorie, gravite=gravite, texte=texte)

def lire_scan(rapport: dict, numero: int, env: str = 'production') -> Signal:
    for k in ('id_faille', 'paquet', 'risque', 'date'):
        if k not in rapport:
            raise ValueError(f'Clé manquante dans rapport scan: {k}')
    id_faille = rapport['id_faille']
    paquet = rapport['paquet']
    risque = str(rapport['risque']).lower()
    date = rapport['date']
    ref = f'SH-{numero:04d}'
    origine = 'SCANNER'
    service = paquet
    categorie = 'FAILLE'
    if risque == 'critique':
        gravite = 'BLOQUANT'
    elif risque == 'haut':
        gravite = 'MAJEUR'
    elif risque == 'moyen':
        gravite = 'MODERE'
    else:
        gravite = 'MINEUR'
    texte = f'Faille {id_faille} dans {paquet}'
    return Signal(ref=ref, date=date, origine=origine, service=service, env=env, categorie=categorie, gravite=gravite, texte=texte)

def lire_build(rapport: dict, numero: int, env: str = 'production') -> Signal:
    for k in ('etape', 'resultat', 'date'):
        if k not in rapport:
            raise ValueError(f'Clé manquante dans rapport build: {k}')
    etape = rapport['etape']
    resultat = rapport['resultat']
    date = rapport['date']
    ref = f'SH-{numero:04d}'
    origine = 'BUILD'
    service = etape
    if str(resultat).lower() == 'echec':
        categorie = 'BUILD_ECHEC'
        gravite = 'MAJEUR'
    else:
        categorie = 'BUILD_OK'
        gravite = 'MINEUR'
    texte = f'Build {etape} : {resultat}'
    return Signal(ref=ref, date=date, origine=origine, service=service, env=env, categorie=categorie, gravite=gravite, texte=texte)
