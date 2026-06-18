# -*- coding: utf-8 -*-
r"""
generar_html.py
=====================
Generador de base de conocimiento HTML para el Mundial FIFA 2026.
Adaptado para ejecución local y automatizaciones basadas en GitHub Actions.
"""

import sys
import datetime
import html
import urllib.parse
import re
import requests
import feedparser

# ============================================================
# CONFIGURACION
# ============================================================
# Se utiliza ruta relativa compatible tanto con Windows local como con entornos Linux Cloud
ARCHIVO_SALIDA = "mundial.html"
TIMEOUT_RSS = 10
MAX_NOTICIAS = 15

# ============================================================
# CONSTANTES: GRUPOS
# ============================================================
GRUPOS = {
    'A': ['MEXICO', 'SUDAFRICA', 'COREA DEL SUR', 'CHEQUIA'],
    'B': ['CANADA', 'BOSNIA HERZEGOVINA', 'QATAR', 'SUIZA'],
    'C': ['BRASIL', 'MARRUECOS', 'HAITI', 'ESCOCIA'],
    'D': ['ESTADOS UNIDOS', 'PARAGUAY', 'AUSTRALIA', 'TURQUIA'],
    'E': ['ALEMANIA', 'CURAZAO', 'COSTA DE MARFIL', 'ECUADOR'],
    'F': ['PAISES BAJOS', 'JAPON', 'SUECIA', 'TUNEZ'],
    'G': ['BELGICA', 'EGIPTO', 'IRAN', 'NUEVA ZELANDA'],
    'H': ['ESPANA', 'CABO VERDE', 'ARABIA SAUDI', 'URUGUAY'],
    'I': ['FRANCIA', 'SENEGAL', 'IRAK', 'NORUEGA'],
    'J': ['ARGENTINA', 'ARGELIA', 'AUSTRIA', 'JORDANIA'],
    'K': ['PORTUGAL', 'RD CONGO', 'UZBEKISTAN', 'COLOMBIA'],
    'L': ['INGLATERRA', 'CROACIA', 'GHANA', 'PANAMA'],
}

# ============================================================
# CONSTANTES: TABLA DE POSICIONES
# ============================================================
POSICIONES = {
    'A': [
        {'equipo': 'MEXICO',         'pj': 1, 'pg': 1, 'pe': 0, 'pp': 0, 'gf': 2, 'gc': 0, 'dg': 2,  'pts': 3},
        {'equipo': 'COREA DEL SUR',  'pj': 1, 'pg': 1, 'pe': 0, 'pp': 0, 'gf': 2, 'gc': 1, 'dg': 1,  'pts': 3},
        {'equipo': 'SUDAFRICA',      'pj': 1, 'pg': 0, 'pe': 0, 'pp': 1, 'gf': 0, 'gc': 2, 'dg': -2, 'pts': 0},
        {'equipo': 'CHEQUIA',        'pj': 1, 'pg': 0, 'pe': 0, 'pp': 1, 'gf': 1, 'gc': 2, 'dg': -1, 'pts': 0},
    ],
    'B': [
        {'equipo': 'CANADA',              'pj': 1, 'pg': 0, 'pe': 1, 'pp': 0, 'gf': 1, 'gc': 1, 'dg': 0, 'pts': 1},
        {'equipo': 'BOSNIA HERZEGOVINA',  'pj': 1, 'pg': 0, 'pe': 1, 'pp': 0, 'gf': 1, 'gc': 1, 'dg': 0, 'pts': 1},
        {'equipo': 'QATAR',               'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'SUIZA',               'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
    'C': [
        {'equipo': 'BRASIL',    'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'MARRUECOS', 'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'HAITI',     'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'ESCOCIA',   'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
    'D': [
        {'equipo': 'ESTADOS UNIDOS', 'pj': 1, 'pg': 1, 'pe': 0, 'pp': 0, 'gf': 4, 'gc': 1, 'dg': 3,  'pts': 3},
        {'equipo': 'PARAGUAY',       'pj': 1, 'pg': 0, 'pe': 0, 'pp': 1, 'gf': 1, 'gc': 4, 'dg': -3, 'pts': 0},
        {'equipo': 'AUSTRALIA',      'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0,  'pts': 0},
        {'equipo': 'TURQUIA',        'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0,  'pts': 0},
    ],
    'E': [
        {'equipo': 'ALEMANIA',        'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'CURAZAO',         'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'COSTA DE MARFIL', 'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'ECUADOR',         'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
    'F': [
        {'equipo': 'PAISES BAJOS', 'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'JAPON',        'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'SUECIA',       'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'TUNEZ',        'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
    'G': [
        {'equipo': 'BELGICA',       'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'EGIPTO',        'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'IRAN',          'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'NUEVA ZELANDA', 'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
    'H': [
        {'equipo': 'ESPANA',       'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'CABO VERDE',   'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'ARABIA SAUDI', 'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'URUGUAY',      'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
    'I': [
        {'equipo': 'FRANCIA',  'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'SENEGAL',  'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'IRAK',     'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'NORUEGA',  'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
    'J': [
        {'equipo': 'ARGENTINA', 'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'ARGELIA',   'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'AUSTRIA',   'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'JORDANIA',  'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
    'K': [
        {'equipo': 'PORTUGAL',   'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'RD CONGO',   'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'UZBEKISTAN', 'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'COLOMBIA',   'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
    'L': [
        {'equipo': 'INGLATERRA', 'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'CROACIA',    'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'GHANA',      'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
        {'equipo': 'PANAMA',     'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0, 'gf': 0, 'gc': 0, 'dg': 0, 'pts': 0},
    ],
}

# ============================================================
# CONSTANTES: RESULTADOS
# ============================================================
RESULTADOS = [
    {
        'fecha': '11/06/2026', 'hora': '16:00', 'grupo': 'A',
        'local': 'MEXICO', 'visitante': 'SUDAFRICA',
        'goles_local': 2, 'goles_visitante': 0,
        'estadio': 'ESTADIO AZTECA, CIUDAD DE MEXICO, MEXICO',
        'goles_detalle': [
            'MIN 09: JULIAN QUINONES (MEX)',
            'MIN 67: RAUL JIMENEZ (MEX)',
        ],
        'amarillas': ['MIN 17: TEBOHO MOKOENA (RSA) - PRIMERA TARJETA AMARILLA DEL TORNEO'],
        'rojas': [
            'MIN 49: SPHEPHELO SITHOLE (RSA) - ROJA DIRECTA (NEGACION DE GOL CLARO)',
            'MIN 84: THEMBA ZWANE (RSA) - ROJA DIRECTA POR VAR (AGRESION A RIVAL)',
            'MIN 90+2: CESAR MONTES (MEX) - ROJA DIRECTA',
        ],
        'nota': 'SUDAFRICA TERMINO CON 9 JUGADORES. ASISTENCIA: APROX. 87.000 ESPECTADORES.',
    },
    {
        'fecha': '11/06/2026', 'hora': '23:00', 'grupo': 'A',
        'local': 'COREA DEL SUR', 'visitante': 'CHEQUIA',
        'goles_local': 2, 'goles_visitante': 1,
        'estadio': 'ESTADIO AKRON, GUADALAJARA, MEXICO',
        'goles_detalle': [
            'MIN 59: LADISLAV KREJCI (CZE)',
            'MIN 67: HWANG INBEOM (KOR) - EMPATE',
            'MIN 80: OH HYEON-GYU (KOR) - GOL DE LA VICTORIA',
        ],
        'amarillas': [],
        'rojas': [],
        'nota': '',
    },
    {
        'fecha': '12/06/2026', 'hora': '22:00', 'grupo': 'D',
        'local': 'ESTADOS UNIDOS', 'visitante': 'PARAGUAY',
        'goles_local': 4, 'goles_visitante': 1,
        'estadio': 'SOFI STADIUM, INGLEWOOD, CALIFORNIA, USA',
        'goles_detalle': [
            'MIN 07: DAMIAN BOBADILLA (PAR) - AUTOGOL',
            'MIN 31: FOLARIN BALOGUN (USA) - ASISTENCIA: CHRISTIAN PULISIC',
            'MIN 45+5: FOLARIN BALOGUN (USA)',
            'MIN 73: MAURICIO MAGALHAES (PAR)',
            'MIN 90+8: GIOVANNI REYNA (USA)',
        ],
        'amarillas': [],
        'rojas': [],
        'nota': 'BALOGUN: PRIMER AMERICANO EN HACER DOBLETE EN UN MUNDIAL DESDE 1930. ASISTENCIA: 70.492 ESPECTADORES.',
    },
    {
        'fecha': '12/06/2026', 'hora': '22:00', 'grupo': 'B',
        'local': 'CANADA', 'visitante': 'BOSNIA HERZEGOVINA',
        'goles_local': 1, 'goles_visitante': 1,
        'estadio': 'BMO FIELD, TORONTO, CANADA',
        'goles_detalle': [
            'MIN 21: JOVO LUKIC (BIH) - CABEZAZO EN CORNER',
            'MIN 78: CYLE LARIN (CAN) - ASISTENCIA: PROMISE DAVID',
        ],
        'amarillas': [],
        'rojas': [],
        'nota': 'PRIMER PUNTO DE CANADA EN UN MUNDIAL SENIOR MASCULINO.',
    },
]

# ============================================================
# CONSTANTES: GOLEADORES
# ============================================================
GOLEADORES = [
    {'jugador': 'FOLARIN BALOGUN',    'seleccion': 'ESTADOS UNIDOS',    'goles': 2},
    {'jugador': 'JULIAN QUINONES',    'seleccion': 'MEXICO',             'goles': 1},
    {'jugador': 'RAUL JIMENEZ',       'seleccion': 'MEXICO',             'goles': 1},
    {'jugador': 'LADISLAV KREJCI',    'seleccion': 'CHEQUIA',            'goles': 1},
    {'jugador': 'HWANG INBEOM',       'seleccion': 'COREA DEL SUR',      'goles': 1},
    {'jugador': 'OH HYEON-GYU',       'seleccion': 'COREA DEL SUR',      'goles': 1},
    {'jugador': 'JOVO LUKIC',         'seleccion': 'BOSNIA HERZEGOVINA', 'goles': 1},
    {'jugador': 'CYLE LARIN',         'seleccion': 'CANADA',             'goles': 1},
    {'jugador': 'GIOVANNI REYNA',     'seleccion': 'ESTADOS UNIDOS',      'goles': 1},
    {'jugador': 'MAURICIO MAGALHAES', 'seleccion': 'PARAGUAY',           'goles': 1},
]

# ============================================================
# CONSTANTES: VALLA MENOS VENCIDA
# ============================================================
VALLA_MENOS_VENCIDA = [
    {'equipo': 'MEXICO',             'pj': 1, 'goles_recibidos': 0},
    {'equipo': 'ESTADOS UNIDOS',     'pj': 1, 'goles_recibidos': 1},
    {'equipo': 'COREA DEL SUR',      'pj': 1, 'goles_recibidos': 1},
    {'equipo': 'CANADA',             'pj': 1, 'goles_recibidos': 1},
    {'equipo': 'BOSNIA HERZEGOVINA', 'pj': 1, 'goles_recibidos': 1},
    {'equipo': 'CHEQUIA',            'pj': 1, 'goles_recibidos': 2},
    {'equipo': 'SUDAFRICA',          'pj': 1, 'goles_recibidos': 2},
    {'equipo': 'PARAGUAY',           'pj': 1, 'goles_recibidos': 4},
]

# ============================================================
# CONSTANTES: TARJETAS
# ============================================================
TARJETAS_AMARILLAS = [
    {'jugador': 'TEBOHO MOKOENA', 'seleccion': 'SUDAFRICA',
     'partido': 'MEXICO VS SUDAFRICA', 'minuto': '17',
     'nota': 'PRIMERA TARJETA AMARILLA DEL TORNEO'},
]

TARJETAS_ROJAS = [
    {'jugador': 'SPHEPHELO SITHOLE', 'seleccion': 'SUDAFRICA',
     'partido': 'MEXICO VS SUDAFRICA', 'minuto': '49',
     'tipo': 'ROJA DIRECTA', 'motivo': 'NEGACION DE GOL CLARO'},
    {'jugador': 'THEMBA ZWANE', 'seleccion': 'SUDAFRICA',
     'partido': 'MEXICO VS SUDAFRICA', 'minuto': '84',
     'tipo': 'ROJA DIRECTA POR VAR', 'motivo': 'AGRESION A RIVAL'},
    {'jugador': 'CESAR MONTES', 'seleccion': 'MEXICO',
     'partido': 'MEXICO VS SUDAFRICA', 'minuto': '90+2',
     'tipo': 'ROJA DIRECTA', 'motivo': 'FALTA SOBRE KHULISO MUDAU'},
]

# ============================================================
# CONSTANTES: SUSPENDIDOS MANUALES (SOBREESCRITURAS FIFA)
# ============================================================
SUSPENDIDOS_MANUALES = []

# ============================================================
# CONSTANTES: LLAVE ELIMINATORIA (ROUND OF 32 ONWARDS)
# ============================================================
LLAVE_ELIMINATORIA = {
    'DIECISEISAVOS DE FINAL (ROUND OF 32)': [],
    'OCTAVOS DE FINAL': [],
    'CUARTOS DE FINAL': [],
    'SEMIFINALES': [],
    'TERCER PUESTO': [],
    'FINAL': []
}

# ============================================================
# CONSTANTES: SELECCION ARGENTINA
# ============================================================
ARGENTINA = {
    'dt': 'LIONEL SCALONI',
    'capitan': 'LIONEL MESSI',
    'subcapitan': 'NICOLAS OTAMENDI',
    'grupo': 'J',
    'concentracion': 'COMPASS MINERALS NATIONAL PERFORMANCE CENTER, KANSAS CITY, USA',
    'arqueros': [
        '1  - EMILIANO "DIBU" MARTINEZ (ASTON VILLA / ING)',
        '12 - JUAN MUSSO (ATALANTA / ITA)',
        '23 - GERONIMO RULLI (AJAX / NED)',
    ],
    'defensores': [
        '2  - NAHUEL MOLINA (ATLETICO MADRID / ESP)',
        '3  - NICOLAS TAGLIAFICO (LYON / FRA)',
        '4  - GONZALO MONTIEL (NOTTINGHAM FOREST / ING)',
        '5  - FACUNDO MEDINA (LENS / FRA)',
        '6  - LISANDRO MARTINEZ (MANCHESTER UNITED / ING)',
        '13 - CRISTIAN ROMERO (TOTTENHAM / ING)',
        '19 - NICOLAS OTAMENDI (BENFICA / POR)',
        '26 - MARCOS SENESI (BOURNEMOUTH / ING)',
    ],
    'mediocampistas': [
        '7  - RODRIGO DE PAUL (ATLETICO MADRID / ESP)',
        '8  - VALENTIN BARCO (BRIGHTON / ING)',
        '9  - EXEQUIEL PALACIOS (BAYER LEVERKUSEN / ALE)',
        '14 - ENZO FERNANDEZ (CHELSEA / ING)',
        '16 - LEANDRO PAREDES (ROMA / ITA) - BAJO SEGUIMIENTO MEDICO',
        '17 - ALEXIS MAC ALLISTER (LIVERPOOL / ING)',
        '18 - NICOLAS PAZ (COMO / ITA)',
        '22 - GIOVANI LO CELSO (BETIS / ESP) - REGRESA TRAS PERDERSE QATAR 2022',
        '25 - THIAGO ALMADA (BOTAFOGO / BRA)',
    ],
    'delanteros': [
        '10 - LIONEL MESSI (INTER MIAMI / USA) - CAPITAN / SEXTO MUNDIAL',
        '11 - NICOLAS GONZALEZ (JUVENTUS / ITA)',
        '15 - GIULIANO SIMEONE (ATLETICO MADRID / ESP)',
        '20 - LAUTARO MARTINEZ (INTER / ITA)',
        '21 - JOSE MANUEL "FLACO" LOPEZ (INDEPENDIENTE)',
        '24 - JULIAN ALVAREZ (ATLETICO MADRID / ESP)',
    ],
    'bajas': [
        'LEONARDO BALERDI (MARSELLA / FRA) - BAJA POR LESION ANTES DEL TORNEO',
    ],
    'novedades': [
        'MESSI PARTICIPA EN SU SEXTO MUNDIAL. SUPERO SOBRECARGA MUSCULAR Y ESTA LISTO.',
        'PAREDES BAJO SEGUIMIENTO MEDICO. DISPONIBILIDAD A CONFIRMAR.',
        'ROMERO, MONTIEL Y MOLINA RECUPERADOS DE DOLENCIAS MENORES.',
        'DIBU MARTINEZ RECUPERADO Y LISTO PARA JUGAR.',
        'AMISTOSOS PREVIOS: ARGENTINA 3-0 ISLANDIA, ARGENTINA VS HONDURAS.',
    ],
    'partidos': [
        {
            'fecha': '16/06/2026', 'dia': 'MARTES', 'hora': '22:00',
            'rival': 'ARGELIA', 'condicion': 'LOCAL',
            'ciudad': 'KANSAS CITY, USA',
            'canales': 'TELEFE (12/1001) + TV PUBLICA (8/999) + TYC SPORTS (106/1018) + DISNEY+ PREMIUM $23.999',
        },
        {
            'fecha': '22/06/2026', 'dia': 'LUNES', 'hora': '14:00',
            'rival': 'AUSTRIA', 'condicion': 'LOCAL',
            'ciudad': 'DALLAS, USA',
            'canales': 'TELEFE (12/1001) + TV PUBLICA (8/999) + TYC SPORTS (106/1018) + DISNEY+ PREMIUM $23.999',
        },
        {
            'fecha': '27/06/2026', 'dia': 'SABADO', 'hora': '23:00',
            'rival': 'JORDANIA', 'condicion': 'VISITANTE',
            'ciudad': 'DALLAS, USA',
            'canales': 'TELEFE (12/1001) + TV PUBLICA (8/999) + TYC SPORTS (106/1018) + DISNEY+ PREMIUM $23.999',
        },
    ],
}

# ============================================================
# CONSTANTES: FIXTURES COMPLETO
# ============================================================
FIXTURES = [
    {'fecha': '11/06/2026', 'hora': '16:00', 'grupo': 'A', 'local': 'MEXICO',          'visitante': 'SUDAFRICA',          'resultado': '2-0', 'jugado': True},
    {'fecha': '11/06/2026', 'hora': '23:00', 'grupo': 'A', 'local': 'COREA DEL SUR',   'visitante': 'CHEQUIA',            'resultado': '2-1', 'jugado': True},
    {'fecha': '12/06/2026', 'hora': '22:00', 'grupo': 'D', 'local': 'ESTADOS UNIDOS',  'visitante': 'PARAGUAY',           'resultado': '4-1', 'jugado': True},
    {'fecha': '12/06/2026', 'hora': '22:00', 'grupo': 'B', 'local': 'CANADA',          'visitante': 'BOSNIA HERZEGOVINA', 'resultado': '1-1', 'jugado': True},
    {'fecha': '13/06/2026', 'hora': '13:00', 'grupo': 'B', 'local': 'QATAR',           'visitante': 'SUIZA',              'resultado': '',    'jugado': False},
    {'fecha': '13/06/2026', 'hora': '19:00', 'grupo': 'C', 'local': 'BRASIL',          'visitante': 'MARRUECOS',          'resultado': '',    'jugado': False},
    {'fecha': '13/06/2026', 'hora': '22:00', 'grupo': 'C', 'local': 'HAITI',           'visitante': 'ESCOCIA',            'resultado': '',    'jugado': False},
    {'fecha': '14/06/2026', 'hora': '01:00', 'grupo': 'D', 'local': 'AUSTRALIA',       'visitante': 'TURQUIA',            'resultado': '',    'jugado': False},
    {'fecha': '14/06/2026', 'hora': '17:00', 'grupo': 'F', 'local': 'PAISES BAJOS',    'visitante': 'JAPON',              'resultado': '',    'jugado': False},
    {'fecha': '14/06/2026', 'hora': '20:00', 'grupo': 'E', 'local': 'COSTA DE MARFIL', 'visitante': 'ECUADOR',            'resultado': '',    'jugado': False},
    {'fecha': '14/06/2026', 'hora': '23:00', 'grupo': 'F', 'local': 'SUECIA',          'visitante': 'TUNEZ',              'resultado': '',    'jugado': False},
    {'fecha': '15/06/2026', 'hora': '16:00', 'grupo': 'G', 'local': 'BELGICA',         'visitante': 'EGIPTO',             'resultado': '',    'jugado': False},
    {'fecha': '15/06/2026', 'hora': '19:00', 'grupo': 'H', 'local': 'ARABIA SAUDI',    'visitante': 'URUGUAY',            'resultado': '',    'jugado': False},
    {'fecha': '15/06/2026', 'hora': '22:00', 'grupo': 'G', 'local': 'IRAN',            'visitante': 'NUEVA ZELANDA',      'resultado': '',    'jugado': False},
    {'fecha': '16/06/2026', 'hora': '19:00', 'grupo': 'I', 'local': 'IRAK',            'visitante': 'NORUEGA',            'resultado': '',    'jugado': False},
    {'fecha': '16/06/2026', 'hora': '22:00', 'grupo': 'J', 'local': 'ARGENTINA',       'visitante': 'ARGELIA',            'resultado': '',    'jugado': False},
    {'fecha': '17/06/2026', 'hora': '01:00', 'grupo': 'J', 'local': 'AUSTRIA',         'visitante': 'JORDANIA',           'resultado': '',    'jugado': False},
    {'fecha': '17/06/2026', 'hora': '17:00', 'grupo': 'L', 'local': 'INGLATERRA',      'visitante': 'CROACIA',            'resultado': '',    'jugado': False},
    {'fecha': '17/06/2026', 'hora': '20:00', 'grupo': 'L', 'local': 'GHANA',           'visitante': 'PANAMA',             'resultado': '',    'jugado': False},
    {'fecha': '17/06/2026', 'hora': '23:00', 'grupo': 'K', 'local': 'UZBEKISTAN',      'visitante': 'COLOMBIA',           'resultado': '',    'jugado': False},
    {'fecha': '18/06/2026', 'hora': '13:00', 'grupo': 'A', 'local': 'CHEQUIA',         'visitante': 'SUDAFRICA',          'resultado': '',    'jugado': False},
    {'fecha': '18/06/2026', 'hora': '16:00', 'grupo': 'B', 'local': 'SUIZA',           'visitante': 'BOSNIA HERZEGOVINA', 'resultado': '',    'jugado': False},
    {'fecha': '18/06/2026', 'hora': '22:00', 'grupo': 'A', 'local': 'MEXICO',          'visitante': 'COREA DEL SUR',      'resultado': '',    'jugado': False},
    {'fecha': '19/06/2026', 'hora': '16:00', 'grupo': 'D', 'local': 'ESTADOS UNIDOS',  'visitante': 'AUSTRALIA',          'resultado': '',    'jugado': False},
    {'fecha': '19/06/2026', 'hora': '19:00', 'grupo': 'C', 'local': 'ESCOCIA',         'visitante': 'MARRUECOS',          'resultado': '',    'jugado': False},
    {'fecha': '19/06/2026', 'hora': '21:30', 'grupo': 'C', 'local': 'BRASIL',          'visitante': 'HAITI',              'resultado': '',    'jugado': False},
    {'fecha': '20/06/2026', 'hora': '14:00', 'grupo': 'F', 'local': 'PAISES BAJOS',    'visitante': 'SUECIA',             'resultado': '',    'jugado': False},
    {'fecha': '20/06/2026', 'hora': '17:00', 'grupo': 'E', 'local': 'ALEMANIA',        'visitante': 'COSTA DE MARFIL',    'resultado': '',    'jugado': False},
    {'fecha': '21/06/2026', 'hora': '13:00', 'grupo': 'H', 'local': 'ESPANA',          'visitante': 'ARABIA SAUDI',       'resultado': '',    'jugado': False},
    {'fecha': '21/06/2026', 'hora': '19:00', 'grupo': 'H', 'local': 'URUGUAY',         'visitante': 'CABO VERDE',         'resultado': '',    'jugado': False},
    {'fecha': '21/06/2026', 'hora': '22:00', 'grupo': 'G', 'local': 'NUEVA ZELANDA',   'visitante': 'EGIPTO',             'resultado': '',    'jugado': False},
    {'fecha': '22/06/2026', 'hora': '14:00', 'grupo': 'J', 'local': 'ARGENTINA',       'visitante': 'AUSTRIA',            'resultado': '',    'jugado': False},
    {'fecha': '22/06/2026', 'hora': '21:00', 'grupo': 'I', 'local': 'NORUEGA',         'visitante': 'SENEGAL',            'resultado': '',    'jugado': False},
    {'fecha': '23/06/2026', 'hora': '14:00', 'grupo': 'K', 'local': 'PORTUGAL',        'visitante': 'UZBEKISTAN',         'resultado': '',    'jugado': False},
    {'fecha': '23/06/2026', 'hora': '17:00', 'grupo': 'L', 'local': 'INGLATERRA',      'visitante': 'GHANA',              'resultado': '',    'jugado': False},
    {'fecha': '23/06/2026', 'hora': '20:00', 'grupo': 'L', 'local': 'PANAMA',          'visitante': 'CROACIA',            'resultado': '',    'jugado': False},
    {'fecha': '24/06/2026', 'hora': '16:00', 'grupo': 'B', 'local': 'SUIZA',           'visitante': 'CANADA',             'resultado': '',    'jugado': False},
    {'fecha': '24/06/2026', 'hora': '19:00', 'grupo': 'C', 'local': 'ESCOCIA',         'visitante': 'BRASIL',             'resultado': '',    'jugado': False},
    {'fecha': '24/06/2026', 'hora': '19:00', 'grupo': 'C', 'local': 'MARRUECOS',       'visitante': 'HAITI',              'resultado': '',    'jugado': False},
    {'fecha': '24/06/2026', 'hora': '22:00', 'grupo': 'A', 'local': 'SUDAFRICA',       'visitante': 'COREA DEL SUR',      'resultado': '',    'jugado': False},
    {'fecha': '25/06/2026', 'hora': '17:00', 'grupo': 'E', 'local': 'ECUADOR',         'visitante': 'ALEMANIA',           'resultado': '',    'jugado': False},
    {'fecha': '25/06/2026', 'hora': '20:00', 'grupo': 'F', 'local': 'JAPON',           'visitante': 'SUECIA',             'resultado': '',    'jugado': False},
    {'fecha': '25/06/2026', 'hora': '23:00', 'grupo': 'D', 'local': 'TURQUIA',         'visitante': 'ESTADOS UNIDOS',     'resultado': '',    'jugado': False},
    {'fecha': '25/06/2026', 'hora': '23:00', 'grupo': 'D', 'local': 'PARAGUAY',        'visitante': 'AUSTRALIA',          'resultado': '',    'jugado': False},
    {'fecha': '26/06/2026', 'hora': '16:00', 'grupo': 'I', 'local': 'NORUEGA',         'visitante': 'FRANCIA',            'resultado': '',    'jugado': False},
    {'fecha': '26/06/2026', 'hora': '21:00', 'grupo': 'H', 'local': 'URUGUAY',         'visitante': 'ESPANA',             'resultado': '',    'jugado': False},
    {'fecha': '27/06/2026', 'hora': '00:00', 'grupo': 'G', 'local': 'EGIPTO',          'visitante': 'IRAN',               'resultado': '',    'jugado': False},
    {'fecha': '27/06/2026', 'hora': '18:00', 'grupo': 'L', 'local': 'PANAMA',          'visitante': 'INGLATERRA',         'resultado': '',    'jugado': False},
    {'fecha': '27/06/2026', 'hora': '20:30', 'grupo': 'K', 'local': 'RD CONGO',        'visitante': 'UZBEKISTAN',         'resultado': '',    'jugado': False},
    {'fecha': '27/06/2026', 'hora': '23:00', 'grupo': 'J', 'local': 'JORDANIA',        'visitante': 'ARGENTINA',          'resultado': '',    'jugado': False},
]

# ============================================================
# CONSTANTES: GRILLA TELECENTRO PLAY
# ============================================================
GRILLA_TELECENTRO = [
    {'dia': 'JUE', 'fecha': '11/06', 'hora': '16:00', 'partido': 'MEXICO VS SUDAFRICA',           'canales': 'TELEFE (12/1001)',                               'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'JUE', 'fecha': '11/06', 'hora': '23:00', 'partido': 'COREA DEL SUR VS CHEQUIA',       'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'VIE', 'fecha': '12/06', 'hora': '22:00', 'partido': 'ESTADOS UNIDOS VS PARAGUAY',     'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'SAB', 'fecha': '13/06', 'hora': '13:00', 'partido': 'QATAR VS SUIZA',                 'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'SAB', 'fecha': '13/06', 'hora': '19:00', 'partido': 'BRASIL VS MARRUECOS',            'canales': 'TELEFE (12/1001)',                               'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'SAB', 'fecha': '13/06', 'hora': '22:00', 'partido': 'HAITI VS ESCOCIA',               'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'DOM', 'fecha': '14/06', 'hora': '01:00', 'partido': 'AUSTRALIA VS TURQUIA',           'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'DOM', 'fecha': '14/06', 'hora': '17:00', 'partido': 'PAISES BAJOS VS JAPON',          'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'DOM', 'fecha': '14/06', 'hora': '20:00', 'partido': 'COSTA DE MARFIL VS ECUADOR',     'canales': 'TELEFE (12/1001)',                               'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'DOM', 'fecha': '14/06', 'hora': '23:00', 'partido': 'SUECIA VS TUNEZ',                'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'LUN', 'fecha': '15/06', 'hora': '16:00', 'partido': 'BELGICA VS EGIPTO',              'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'LUN', 'fecha': '15/06', 'hora': '19:00', 'partido': 'ARABIA SAUDI VS URUGUAY',        'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'LUN', 'fecha': '15/06', 'hora': '22:00', 'partido': 'RI DE IRAN VS NUEVA ZELANDA',    'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'MAR', 'fecha': '16/06', 'hora': '19:00', 'partido': 'IRAK VS NORUEGA',                'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'MAR', 'fecha': '16/06', 'hora': '22:00', 'partido': 'ARGENTINA VS ARGELIA',           'canales': 'TELEFE (12/1001) + TV PUBLICA (8/999) + TyC Sports (106/1018)', 'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': True},
    {'dia': 'MIE', 'fecha': '17/06', 'hora': '01:00', 'partido': 'AUSTRIA VS JORDANIA',            'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'MIE', 'fecha': '17/06', 'hora': '17:00', 'partido': 'INGLATERRA VS CROACIA',          'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'MIE', 'fecha': '17/06', 'hora': '20:00', 'partido': 'GHANA VS PANAMA',                'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'MIE', 'fecha': '17/06', 'hora': '23:00', 'partido': 'UZBEKISTAN VS COLOMBIA',         'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'JUE', 'fecha': '18/06', 'hora': '13:00', 'partido': 'CHEQUIA VS SUDAFRICA',           'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'JUE', 'fecha': '18/06', 'hora': '16:00', 'partido': 'SUIZA VS BOSNIA HERZEGOVINA',    'canales': 'TELEFE (12/1001)',                               'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'JUE', 'fecha': '18/06', 'hora': '22:00', 'partido': 'MEXICO VS COREA DEL SUR',        'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'VIE', 'fecha': '19/06', 'hora': '16:00', 'partido': 'ESTADOS UNIDOS VS AUSTRALIA',    'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'VIE', 'fecha': '19/06', 'hora': '19:00', 'partido': 'ESCOCIA VS MARRUECOS',            'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'VIE', 'fecha': '19/06', 'hora': '21:30', 'partido': 'BRASIL VS HAITI',                'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'SAB', 'fecha': '20/06', 'hora': '14:00', 'partido': 'PAISES BAJOS VS SUECIA',          'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'SAB', 'fecha': '20/06', 'hora': '17:00', 'partido': 'ALEMANIA VS COSTA DE MARFIL',    'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'DOM', 'fecha': '21/06', 'hora': '13:00', 'partido': 'ESPANA VS ARABIA SAUDI',          'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'DOM', 'fecha': '21/06', 'hora': '19:00', 'partido': 'URUGUAY VS CABO VERDE',          'canales': 'TELEFE (12/1001)',                               'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'DOM', 'fecha': '21/06', 'hora': '22:00', 'partido': 'NUEVA ZELANDA VS EGIPTO',        'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'LUN', 'fecha': '22/06', 'hora': '14:00', 'partido': 'ARGENTINA VS AUSTRIA',           'canales': 'TELEFE (12/1001) + TV PUBLICA (8/999) + TyC Sports (106/1018)', 'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': True},
    {'dia': 'LUN', 'fecha': '22/06', 'hora': '21:00', 'partido': 'NORUEGA VS SENEGAL',             'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'MAR', 'fecha': '23/06', 'hora': '14:00', 'partido': 'PORTUGAL VS UZBEKISTAN',         'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'MAR', 'fecha': '23/06', 'hora': '17:00', 'partido': 'INGLATERRA VS GHANA',            'canales': 'TELEFE (12/1001)',                               'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'MAR', 'fecha': '23/06', 'hora': '20:00', 'partido': 'PANAMA VS CROACIA',              'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'MIE', 'fecha': '24/06', 'hora': '16:00', 'partido': 'SUIZA VS CANADA',                'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'MIE', 'fecha': '24/06', 'hora': '19:00', 'partido': 'ESCOCIA VS BRASIL',              'canales': 'TELEFE (12/1001)',                               'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'MIE', 'fecha': '24/06', 'hora': '19:00', 'partido': 'MARRUECOS VS HAITI',              'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'MIE', 'fecha': '24/06', 'hora': '22:00', 'partido': 'SUDAFRICA VS COREA DEL SUR',     'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'JUE', 'fecha': '25/06', 'hora': '17:00', 'partido': 'ECUADOR VS ALEMANIA',            'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'JUE', 'fecha': '25/06', 'hora': '20:00', 'partido': 'JAPON VS SUECIA',                'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'JUE', 'fecha': '25/06', 'hora': '23:00', 'partido': 'TURQUIA VS ESTADOS UNIDOS',      'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'JUE', 'fecha': '25/06', 'hora': '23:00', 'partido': 'PARAGUAY VS AUSTRALIA',          'canales': 'TELEFE (12/1001)',                               'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'VIE', 'fecha': '26/06', 'hora': '16:00', 'partido': 'NORUEGA VS FRANCIA',             'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'VIE', 'fecha': '26/06', 'hora': '21:00', 'partido': 'URUGUAY VS ESPANA',              'canales': 'TELEFE (12/1001) + TyC Sports (106/1018)',       'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': False},
    {'dia': 'SAB', 'fecha': '27/06', 'hora': '00:00', 'partido': 'EGIPTO VS RI DE IRAN',           'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'SAB', 'fecha': '27/06', 'hora': '18:00', 'partido': 'PANAMA VS INGLATERRA',           'canales': 'TV PUBLICA (8/999) + TyC Sports (106/1018)',      'sva': '',                         'argentina': False},
    {'dia': 'SAB', 'fecha': '27/06', 'hora': '20:30', 'partido': 'RD CONGO VS UZBEKISTAN',         'canales': 'TyC Sports (106/1018)',                           'sva': '',                         'argentina': False},
    {'dia': 'SAB', 'fecha': '27/06', 'hora': '23:00', 'partido': 'JORDANIA VS ARGENTINA',          'canales': 'TELEFE (12/1001) + TV PUBLICA (8/999) + TyC Sports (106/1018)', 'sva': 'DISNEY+ PREMIUM $23.999', 'argentina': True},
]

# ============================================================
# CONSTANTES: CONSULTA RSS UNIFICADA (GOOGLE NEWS FILTRADO)
# ============================================================
QUERY_RSS_UNIFICADA = "seleccion argentina mundial 2026 (site:ole.com.ar OR site:clarin.com OR site:lanacion.com.ar OR site:infobae.com OR site:tycsports.com)"

# ============================================================
# CONSTANTES: FAQ
# ============================================================
FAQ = [
    ('CUANDO DEBUTA ARGENTINA EN EL MUNDIAL 2026?',
     'ARGENTINA DEBUTA EL MARTES 16 DE JUNIO DE 2026 A LAS 22:00 (HORA ARGENTINA) FRENTE A ARGELIA EN KANSAS CITY, USA.'),
    ('EN QUE GRUPO ESTA ARGENTINA?',
     'ARGENTINA INTEGRA EL GRUPO J JUNTO A ARGELIA, AUSTRIA Y JORDANIA.'),
    ('CUANTOS PARTIDOS JUEGA ARGENTINA EN LA FASE DE GRUPOS?',
     'ARGENTINA JUEGA 3 PARTIDOS: VS ARGELIA (16/06 A LAS 22:00), VS AUSTRIA (22/06 A LAS 14:00) Y VS JORDANIA (27/06 A LAS 23:00).'),
    ('QUIEN ES EL DIRECTOR TECNICO DE ARGENTINA?',
     'LIONEL SCALONI ES EL DT DE LA SELECCION ARGENTINA.'),
    ('QUIEN ES EL CAPITAN DE ARGENTINA?',
     'LIONEL MESSI ES EL CAPITAN. ES SU SEXTO Y POSIBLEMENTE ULTIMO MUNDIAL.'),
    ('POR QUE CANAL SE VE ARGENTINA EN EL MUNDIAL?',
     'LOS PARTIDOS DE ARGENTINA SE VEN POR TELEFE (CH 12 / 1001 HD), TV PUBLICA (CH 8 / 999 HD) Y TYC SPORTS (CH 106 / 1018 HD). TAMBIEN POR DISNEY+ PREMIUM ($23.999/MES). EN TELECENTRO PLAY LOS 3 PARTIDOS TIENEN COBERTURA MULTIPLE.'),
    ('A QUE HORA ES EL PARTIDO DE ARGENTINA VS ARGELIA?',
     'EL MARTES 16 DE JUNIO DE 2026 A LAS 22:00 HORA ARGENTINA. EN KANSAS CITY, USA.'),
    ('A QUE HORA ES EL PARTIDO DE ARGENTINA VS AUSTRIA?',
     'EL LUNES 22 DE JUNIO DE 2026 A LAS 14:00 HORA ARGENTINA. EN DALLAS, USA.'),
    ('A QUE HORA ES EL PARTIDO DE JORDANIA VS ARGENTINA?',
     'EL SABADO 27 DE JUNIO DE 2026 A LAS 23:00 HORA ARGENTINA. EN DALLAS, USA.'),
    ('CUANTOS EQUIPOS PARTICIPAN EN EL MUNDIAL 2026?',
     '48 SELECCIONES PARTICIPAN EN EL MUNDIAL 2026, DISTRIBUIDAS EN 12 GRUPOS DE 4 EQUIPOS.'),
    ('COMO ES EL FORMATO DEL MUNDIAL 2026?',
     'FASE DE GRUPOS: 12 GRUPOS DE 4 EQUIPOS. CLASIFICAN LOS 2 PRIMEROS DE CADA GRUPO MAS LOS 8 MEJORES TERCEROS (32 EQUIPOS EN TOTAL A OCTAVOS). LUEGO ELIMINACION DIRECTA HASTA LA FINAL.'),
    ('DONDE SE JUEGA EL MUNDIAL 2026?',
     'EN ESTADOS UNIDOS, MEXICO Y CANADA. ES EL PRIMER MUNDIAL EN 3 PAISES. LA FINAL SE JUEGA EN NEW YORK/NEW JERSEY EL 19 DE JULIO DE 2026.'),
    ('CUANDO TERMINA EL MUNDIAL 2026?',
     'LA FINAL ES EL 19 DE JULIO DE 2026 EN EL METLIFE STADIUM, NEW YORK/NEW JERSEY.'),
    ('QUIEN ES EL MAXIMO GOLEADOR DEL MUNDIAL?',
     'AL 13/06: FOLARIN BALOGUN (USA) CON 2 GOLES. VARIOS JUGADORES CON 1 GOL: QUINONES Y JIMENEZ (MEX), KREJCI (CZE), HWANG INBEOM Y OH HYEON-GYU (KOR), LUKIC (BIH), LARIN (CAN), G. REYNA (USA), MAGALHAES (PAR).'),
    ('QUE PARTIDOS SE JUGARON HASTA AHORA?',
     'AL 13/06: MEXICO 2-0 SUDAFRICA (Grp A), COREA DEL SUR 2-1 CHEQUIA (Grp A), ESTADOS UNIDOS 4-1 PARAGUAY (Grp D), CANADA 1-1 BOSNIA HERZEGOVINA (Grp B).'),
    ('DONDE JUEGA ARGENTINA LOS PARTIDOS DE LA FASE DE GRUPOS?',
     'PARTIDO 1 (VS ARGELIA): KANSAS CITY, USA. PARTIDO 2 (VS AUSTRIA) Y PARTIDO 3 (VS JORDANIA): DALLAS, USA.'),
    ('QUE CANAL ES TELEFE EN TELECENTRO?',
     'TELEFE ESTA EN EL CANAL 12 (SD) Y CANAL 1001 (HD) EN TELECENTRO PLAY.'),
    ('QUE CANAL ES TYC SPORTS EN TELECENTRO?',
     'TYC SPORTS ESTA EN EL CANAL 106 (SD) Y CANAL 1018 (HD) EN TELECENTRO PLAY.'),
    ('QUE CANAL ES TV PUBLICA EN TELECENTRO?',
     'TV PUBLICA ESTA EN EL CANAL 8 (SD) Y CANAL 999 (HD) EN TELECENTRO PLAY.'),
    ('CUANTO CUESTA DISNEY PLUS PREMIUM EN TELECENTRO?',
     'DISNEY+ PREMIUM CUESTA $23.999 ARS POR MES EN TELECENTRO PLAY.'),
    ('CUANTOS JUGADORES LLEVA ARGENTINA AL MUNDIAL?',
     'ARGENTINA LLEVA 26 JUGADORES: 3 ARQUEROS, 8 DEFENSORES, 9 MEDIOCAMPISTAS Y 6 DELANTEROS. BALERDI DIO DE BAJA POR LESION.'),
    ('TIENE TYC SPORTS TODOS LOS PARTIDOS DEL MUNDIAL?',
     'TYC SPORTS TRANSMITE LA MAYORIA DE LOS PARTIDOS. PARA LOS PARTIDOS DE ARGENTINA, SE SUMA TELEFE Y TV PUBLICA (SEÑAL ABIERTA). VER LA GRILLA COMPLETA EN LA SECCION TRANSMISIONES TELECENTRO PLAY.'),
    ('DONDE ESTA CONCENTRADA ARGENTINA?',
     'ARGENTINA ESTA CONCENTRADA EN EL COMPASS MINERALS NATIONAL PERFORMANCE CENTER, KANSAS CITY, USA.'),
    ('QUIEN ES EL SUBCAPITAN DE ARGENTINA?',
     'NICOLAS OTAMENDI ES EL SUBCAPITAN DE LA SELECCION ARGENTINA.'),
    ('CUAL ES EL RESULTADO DEL PRIMER PARTIDO DEL MUNDIAL?',
     'EL PRIMER PARTIDO FUE MEXICO 2-0 SUDAFRICA, EL 11/06/2026 EN EL ESTADIO AZTECA. SUDAFRICA TERMINO CON 9 JUGADORES.'),
]

# ============================================================
# FUNCION: OBTENER NOTICIAS RSS
# ============================================================
def obtener_noticias_rss():
    """Lee noticias a través de la consulta RSS consolidada de Google News AR."""
    noticias = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
    }

    try:
        print("  [RSS] Consultando feed unificado en Google News AR...")
        url_encoded_query = urllib.parse.quote(QUERY_RSS_UNIFICADA)
        url = f"https://news.google.com/rss/search?q={url_encoded_query}&hl=es-419&gl=AR&ceid=AR:es-419"
        
        resp = requests.get(url, timeout=TIMEOUT_RSS, headers=headers)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        print(f"  [RSS] Total de noticias detectadas: {len(feed.entries)}")
        
        for entry in feed.entries[:MAX_NOTICIAS]:
            titulo = getattr(entry, 'title', '').strip()
            descripcion = (getattr(entry, 'summary', '') or
                           getattr(entry, 'description', '') or '').strip()
            
            # Limpiar tags HTML de la descripción
            descripcion = re.sub(r'<[^>]+>', '', descripcion)
            descripcion = descripcion[:300].strip()

            fecha_pub = ''
            if hasattr(entry, 'published') and entry.published:
                fecha_pub = str(entry.published)[:25]
            elif hasattr(entry, 'updated') and entry.updated:
                fecha_pub = str(entry.updated)[:25]

            # Obtener la fuente de origen
            fuente = "Medio Local"
            if hasattr(entry, 'source') and entry.source:
                fuente = entry.source.get('title', 'Medio Local')
            else:
                partes_titulo = titulo.rsplit(" - ", 1)
                if len(partes_titulo) > 1:
                    fuente = partes_titulo[1].strip()

            if titulo:
                noticias.append({
                    'fuente': fuente,
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'fecha': fecha_pub,
                    'link': getattr(entry, 'link', ''),
                })

        print(f"  [RSS] Se procesaron {len(noticias)} noticias con éxito.")

    except requests.exceptions.Timeout:
        print("  [RSS] TIMEOUT al conectarse a Google News RSS.")
    except requests.exceptions.ConnectionError:
        print("  [RSS] ERROR DE CONEXION al conectarse a Google News RSS.")
    except Exception as ex:
        print(f"  [RSS] ERROR inesperado: {ex}")

    return noticias

# ============================================================
# HELPERS
# ============================================================
def e(texto):
    """Escape HTML seguro."""
    return html.escape(str(texto))


def parse_fecha(fecha_str):
    """Convierte DD/MM/YYYY a objeto date."""
    try:
        return datetime.datetime.strptime(fecha_str, "%d/%m/%Y").date()
    except Exception:
        return None


def get_partidos_hoy(fecha_hoy):
    return [p for p in FIXTURES if parse_fecha(p['fecha']) == fecha_hoy]


def get_proximos_partidos(fecha_hoy, dias=7):
    desde = fecha_hoy + datetime.timedelta(days=1)
    hasta = fecha_hoy + datetime.timedelta(days=dias)
    return [
        p for p in FIXTURES
        if not p['jugado']
        and parse_fecha(p['fecha']) is not None
        and desde <= parse_fecha(p['fecha']) <= hasta
    ]


def get_en_vivo(fecha_hoy, hora_actual):
    """Detecta partidos en curso (heurística: entre inicio y +2h)."""
    en_vivo = []
    for p in get_partidos_hoy(fecha_hoy):
        if not p['jugado']:
            try:
                h, m = map(int, p['hora'].split(':'))
                inicio = datetime.datetime.combine(fecha_hoy, datetime.time(h, m))
                fin_aprox = inicio + datetime.timedelta(hours=2)
                ahora = datetime.datetime.combine(fecha_hoy, hora_actual)
                if inicio <= ahora <= fin_aprox:
                     en_vivo.append(p)
            except Exception:
                pass
    return en_vivo


def obtener_suspendidos():
    """Calcula automáticamente los suspendidos en base a tarjetas y overrides manuales."""
    suspendidos = []
    
    # 1. Agregar expulsados (tarjetas rojas en partidos disputados)
    for r in TARJETAS_ROJAS:
        suspendidos.append({
            'jugador': r['jugador'],
            'seleccion': r['seleccion'],
            'motivo': f"EXPULSION (Tarjeta Roja en {r['partido']}, Minuto {r['minuto']}). Motivo: {r['motivo']}"
        })
    
    # 2. Calcular acumuladas (2 amarillas en partidos distintos antes de semifinales)
    amarillas_por_jugador = {}
    for a in TARJETAS_AMARILLAS:
        clave = (a['jugador'], a['seleccion'])
        if clave not in amarillas_por_jugador:
            amarillas_por_jugador[clave] = set()
        amarillas_por_jugador[clave].add(a['partido'])
    
    for (jugador, seleccion), partidos in amarillas_por_jugador.items():
        if len(partidos) >= 2:
            suspendidos.append({
                'jugador': jugador,
                'seleccion': seleccion,
                'motivo': f"ACUMULACION DE TARJETAS AMARILLAS (2 amarillas en partidos distintos: {', '.join(partidos)})"
            })
            
    # 3. Agregar manuales
    for sm in SUSPENDIDOS_MANUALES:
        if not any(s['jugador'] == sm['jugador'] and s['seleccion'] == sm['seleccion'] for s in suspendidos):
            suspendidos.append({
                'jugador': sm['jugador'],
                'seleccion': sm['seleccion'],
                'motivo': sm['motivo']
            })
            
    return suspendidos

# ============================================================
# SECCIONES HTML
# ============================================================
def sec(nombre):
    return f"\n\n", f"\n\n"


def bloque(nombre, contenido):
    ini, fin = sec(nombre)
    return ini + contenido + fin


def generar_estado_torneo():
    c = []
    c.append("<h2>ESTADO DEL TORNEO</h2>")
    c.append("<ul>")
    c.append("<li><strong>TORNEO:</strong> FIFA WORLD CUP 2026</li>")
    c.append("<li><strong>FASE ACTUAL:</strong> FASE DE GRUPOS - JORNADA 1</li>")
    c.append("<li><strong>EDICION:</strong> 23 COPA DEL MUNDO FIFA</li>")
    c.append("<li><strong>FORMATO:</strong> 48 SELECCIONES - 12 GRUPOS (A a L) - 104 PARTIDOS EN TOTAL</li>")
    c.append("<li><strong>SEDES:</strong> ESTADOS UNIDOS, MEXICO Y CANADA (3 PAISES SEDE)</li>")
    c.append("<li><strong>INICIO:</strong> 11 DE JUNIO DE 2026</li>")
    c.append("<li><strong>FINAL:</strong> 19 DE JULIO DE 2026 - METLIFE STADIUM, NEW YORK/NEW JERSEY</li>")
    c.append("<li><strong>PARTIDOS COMPLETADOS AL 13/06:</strong> 4</li>")
    c.append("</ul>")
    c.append("<h3>CIUDADES SEDE</h3><ul>")
    c.append("<li><strong>ESTADOS UNIDOS (11 ciudades):</strong> New York/New Jersey, Los Angeles, Dallas, San Francisco, Seattle, Boston, Miami, Atlanta, Houston, Kansas City, Philadelphia</li>")
    c.append("<li><strong>MEXICO (3 ciudades):</strong> Ciudad de México (Estadio Azteca), Guadalajara, Monterrey</li>")
    c.append("<li><strong>CANADA (2 ciudades):</strong> Toronto (BMO Field), Vancouver</li>")
    c.append("</ul>")
    c.append("<h3>HITOS HISTORICOS DE ESTA EDICION</h3><ul>")
    c.append("<li>PRIMERA EDICION CON 48 SELECCIONES PARTICIPANTES</li>")
    c.append("<li>PRIMERA EDICION CON 3 PAISES ORGANIZADORES</li>")
    c.append("<li>PRIMERA EDICION CON 12 GRUPOS EN FASE INICIAL</li>")
    c.append("<li>CLASIFICAN LOS 2 PRIMEROS DE CADA GRUPO MAS LOS 8 MEJORES TERCEROS (32 TOTAL A OCTAVOS)</li>")
    c.append("</ul>")
    return bloque("ESTADO DEL TORNEO", "\n".join(c))


def generar_partidos_hoy(fecha_hoy):
    c = []
    c.append("<h2>PARTIDOS DE HOY</h2>")
    partidos = get_partidos_hoy(fecha_hoy)
    if not partidos:
        c.append("<p>NO HAY PARTIDOS PROGRAMADOS PARA HOY.</p>")
    else:
        c.append(f"<p><strong>FECHA: {fecha_hoy.strftime('%d/%m/%Y')}</strong></p>")
        c.append("<ul>")
        for p in partidos:
            estado = "COMPLETADO" if p['jugado'] else "PENDIENTE"
            res = f" | RESULTADO: {p['resultado']}" if p['jugado'] and p['resultado'] else ""
            arg = " *** ARG ***" if ('ARGENTINA' in p['local'] or 'ARGENTINA' in p['visitante']) else ""
            c.append(f"<li>{e(p['hora'])} ARG | GRP {e(p['grupo'])} | "
                     f"{e(p['local'])} VS {e(p['visitante'])}{e(res)}{e(arg)} | {estado}</li>")
        c.append("</ul>")
    return bloque("PARTIDOS DE HOY", "\n".join(c))


def generar_en_vivo(fecha_hoy, hora_actual):
    c = []
    c.append("<h2>PARTIDOS EN VIVO</h2>")
    en_vivo = get_en_vivo(fecha_hoy, hora_actual)
    if not en_vivo:
        c.append("<p>NO HAY PARTIDOS EN CURSO EN ESTE MOMENTO (SEGUN HORARIO DE ACTUALIZACION).</p>")
        c.append("<p>CONSULTAR SECCION PARTIDOS DE HOY PARA VER PROGRAMACION COMPLETA DEL DIA.</p>")
    else:
        c.append("<ul>")
        for p in en_vivo:
            c.append(f"<li>[EN VIVO] {e(p['hora'])} ARG | GRP {e(p['grupo'])} | "
                     f"{e(p['local'])} VS {e(p['visitante'])}</li>")
        c.append("</ul>")
    return bloque("PARTIDOS EN VIVO", "\n".join(c))


def generar_proximos_partidos(fecha_hoy):
    c = []
    c.append("<h2>PROXIMOS PARTIDOS (PROXIMOS 7 DIAS)</h2>")
    proximos = get_proximos_partidos(fecha_hoy, dias=7)
    if not proximos:
        c.append("<p>NO HAY PROXIMOS PARTIDOS EN LOS SIGUIENTES 7 DIAS.</p>")
    else:
        fecha_ant = None
        for p in proximos:
            if p['fecha'] != fecha_ant:
                if fecha_ant is not None:
                    c.append("</ul>")
                fecha_ant = p['fecha']
                c.append(f"<h3>{e(p['fecha'])}</h3><ul>")
            arg = " *** PARTIDO DE ARGENTINA ***" if ('ARGENTINA' in p['local'] or 'ARGENTINA' in p['visitante']) else ""
            c.append(f"<li>{e(p['hora'])} ARG | GRP {e(p['grupo'])} | "
                     f"{e(p['local'])} VS {e(p['visitante'])}{e(arg)}</li>")
        c.append("</ul>")
    return bloque("PROXIMOS PARTIDOS", "\n".join(c))


def generar_ultimos_resultados():
    c = []
    c.append("<h2>ULTIMOS RESULTADOS</h2>")
    c.append("<p>PARTIDOS COMPLETADOS AL 13/06/2026:</p>")
    for i, r in enumerate(RESULTADOS, 1):
        c.append(f"<h3>PARTIDO {i} - GRUPO {e(r['grupo'])} | {e(r['fecha'])} {e(r['hora'])} ARG</h3>")
        c.append(f"<p><strong>{e(r['local'])} {r['goles_local']} - {r['goles_visitante']} {e(r['visitante'])}</strong></p>")
        c.append(f"<p>ESTADIO: {e(r['estadio'])}</p>")
        if r['goles_detalle']:
            c.append("<p><strong>GOLES:</strong></p><ul>")
            for g in r['goles_detalle']:
                c.append(f"<li>{e(g)}</li>")
            c.append("</ul>")
        if r['amarillas']:
            c.append("<p><strong>TARJETAS AMARILLAS:</strong></p><ul>")
            for a in r['amarillas']:
                c.append(f"<li>{e(a)}</li>")
            c.append("</ul>")
        if r['rojas']:
            c.append("<p><strong>TARJETAS ROJAS:</strong></p><ul>")
            for rj in r['rojas']:
                c.append(f"<li>{e(rj)}</li>")
            c.append("</ul>")
        if r['nota']:
            c.append(f"<p><em>NOTA: {e(r['nota'])}</em></p>")
    return bloque("ULTIMOS RESULTADOS", "\n".join(c))


def generar_grupos():
    c = []
    c.append("<h2>GRUPOS Y TABLAS DE POSICIONES</h2>")
    c.append("<p>ACTUALIZADO AL 13/06/2026. SOLO GRUPOS CON PARTIDOS JUGADOS MUESTRAN POSICIONES.</p>")
    for letra, equipos in GRUPOS.items():
        c.append(f"<h3>GRUPO {letra}</h3>")
        c.append("<p><strong>INTEGRANTES:</strong></p><ul>")
        for eq in equipos:
            suf = " (SEDE)" if eq in ['MEXICO', 'ESTADOS UNIDOS', 'CANADA'] else ""
            c.append(f"<li>{e(eq)}{suf}</li>")
        c.append("</ul>")
        pos_data = POSICIONES.get(letra, [])
        jugados = any(t['pj'] > 0 for t in pos_data)
        if jugados:
            c.append("<p><strong>TABLA DE POSICIONES:</strong> PJ PG PE PP GF GC DG PTS</p><ul>")
            for t in pos_data:
                dg_str = f"+{t['dg']}" if t['dg'] > 0 else str(t['dg'])
                c.append(f"<li>{e(t['equipo'])} | PJ:{t['pj']} PG:{t['pg']} PE:{t['pe']} "
                         f"PP:{t['pp']} GF:{t['gf']} GC:{t['gc']} DG:{dg_str} PTS:{t['pts']}</li>")
            c.append("</ul>")
        else:
            c.append("<p>SIN PARTIDOS JUGADOS AUN EN ESTE GRUPO.</p>")
    return bloque("GRUPOS", "\n".join(c))


def generar_llave_eliminatoria():
    c = []
    c.append("<h2>LLAVE ELIMINATORIA (FASE DE ELIMINACION DIRECTA)</h2>")
    
    hay_partidos = False
    for fase, partidos in LLAVE_ELIMINATORIA.items():
        if partidos:
            hay_partidos = True
            c.append(f"<h3>{e(fase)}</h3>")
            c.append("<ul>")
            for p in partidos:
                estado = "COMPLETADO" if p.get('jugado') else "PENDIENTE"
                res = f" | RESULTADO: {p['resultado']}" if p.get('jugado') and p.get('resultado') else ""
                canales = f" | CANALES: {p['canales']}" if p.get('canales') else ""
                c.append(f"<li>{e(p['fecha'])} {e(p['hora'])} ARG | {e(p['partido'])}{res}{canales} | {estado}</li>")
            c.append("</ul>")
            
    if not hay_partidos:
        c.append("<p>LA FASE DE ELIMINACION DIRECTA AUN NO HA SIDO DEFINIDA.</p>")
        c.append("<p>CLASIFICAN LOS 2 PRIMEROS DE CADA GRUPO (GRUPOS A A L) MAS LOS 8 MEJORES TERCEROS PARA CONFORMAR LOS DIECISEISAVOS DE FINAL (ROUND OF 32).</p>")
        
    return bloque("LLAVE ELIMINATORIA", "\n".join(c))


def generar_goleadores():
    c = []
    c.append("<h2>TABLA DE GOLEADORES</h2>")
    c.append("<p>ACTUALIZADO AL 13/06/2026 (TRAS 4 PARTIDOS JUGADOS)</p>")
    c.append("<ul>")
    for i, g in enumerate(GOLEADORES, 1):
        c.append(f"<li>{i}. {e(g['jugador'])} ({e(g['seleccion'])}) - {g['goles']} GOL{'ES' if g['goles'] != 1 else ''}</li>")
    c.append("</ul>")
    c.append("<p><em>NOTA: LOS AUTOGOLES NO CUENTAN PARA EL RANKING.</em></p>")
    c.append("<p><em>AUTOGOL DEL TORNEO: DAMIAN BOBADILLA (PARAGUAY) EN USA VS PARAGUAY.</em></p>")
    return bloque("GOLEADORES", "\n".join(c))


def generar_valla():
    c = []
    c.append("<h2>VALLA MENOS VENCIDA</h2>")
    c.append("<p>ACTUALIZADO AL 13/06/2026</p>")
    c.append("<ul>")
    for v in sorted(VALLA_MENOS_VENCIDA, key=lambda x: x['goles_recibidos']):
        c.append(f"<li>{e(v['equipo'])} - {v['goles_recibidos']} GOLES RECIBIDOS (PJ: {v['pj']})</li>")
    c.append("</ul>")
    return bloque("VALLA MENOS VENCIDA", "\n".join(c))


def generar_tarjetas_amarillas():
    c = []
    c.append("<h2>TARJETAS AMARILLAS</h2>")
    c.append("<p>ACTUALIZADO AL 13/06/2026</p>")
    c.append("<ul>")
    for t in TARJETAS_AMARILLAS:
        nota = f" ({e(t.get('nota', ''))})" if t.get('nota') else ""
        c.append(f"<li>{e(t['jugador'])} ({e(t['seleccion'])}) - MIN {e(t['minuto'])} - {e(t['partido'])}{nota}</li>")
    c.append("</ul>")
    return bloque("TARJETAS AMARILLAS", "\n".join(c))


def generar_tarjetas_rojas():
    c = []
    c.append("<h2>TARJETAS ROJAS</h2>")
    c.append("<p>ACTUALIZADO AL 13/06/2026</p>")
    c.append("<ul>")
    for t in TARJETAS_ROJAS:
        c.append(f"<li>{e(t['jugador'])} ({e(t['seleccion'])}) - MIN {e(t['minuto'])} - "
                 f"{e(t['tipo'])} - {e(t['partido'])} - MOTIVO: {e(t['motivo'])}</li>")
    c.append("</ul>")
    return bloque("TARJETAS ROJAS", "\n".join(c))


def generar_jugadores_suspendidos():
    c = []
    c.append("<h2>JUGADORES SUSPENDIDOS</h2>")
    c.append("<p>JUGADORES QUE NO PUEDEN DISPUTAR EL PROXIMO PARTIDO (SANCIONES FIFA):</p>")
    
    suspendidos = obtener_suspendidos()
    if not suspendidos:
        c.append("<p>NO HAY JUGADORES SUSPENDIDOS PARA EL SIGUIENTE ENCUENTRO EN ESTE MOMENTO.</p>")
    else:
        c.append("<ul>")
        for s in suspendidos:
            c.append(f"<li><strong>{e(s['jugador'])}</strong> ({e(s['seleccion'])}) - {e(s['motivo'])}</li>")
        c.append("</ul>")
        
    return bloque("JUGADORES SUSPENDIDOS", "\n".join(c))


def generar_seleccion_argentina():
    c = []
    arg = ARGENTINA
    c.append("<h2>SELECCION ARGENTINA - MUNDIAL FIFA 2026</h2>")
    c.append("<ul>")
    c.append(f"<li><strong>DT:</strong> {e(arg['dt'])}</li>")
    c.append(f"<li><strong>CAPITAN:</strong> {e(arg['capitan'])}</li>")
    c.append(f"<li><strong>SUBCAPITAN:</strong> {e(arg['subcapitan'])}</li>")
    c.append(f"<li><strong>GRUPO:</strong> {e(arg['grupo'])}</li>")
    c.append(f"<li><strong>CONCENTRACION:</strong> {e(arg['concentracion'])}</li>")
    c.append("</ul>")
    c.append("<h3>PARTIDOS DE ARGENTINA - FASE DE GRUPOS</h3><ul>")
    for p in arg['partidos']:
        c.append(f"<li><strong>{e(p['dia'])} {e(p['fecha'])} {e(p['hora'])} ARG</strong> | "
                 f"ARGENTINA ({e(p['condicion'])}) VS {e(p['rival'])} | {e(p['ciudad'])}</li>")
        c.append(f"<li>&nbsp;&nbsp;&nbsp;CANALES: {e(p['canales'])}</li>")
    c.append("</ul>")
    c.append("<h3>PLANTEL COMPLETO (26 JUGADORES)</h3>")
    c.append("<h4>ARQUEROS (3)</h4><ul>")
    for j in arg['arqueros']:
        c.append(f"<li>{e(j)}</li>")
    c.append("</ul>")
    c.append("<h4>DEFENSORES (8)</h4><ul>")
    for j in arg['defensores']:
        c.append(f"<li>{e(j)}</li>")
    c.append("</ul>")
    c.append("<h4>MEDIOCAMPISTAS (9)</h4><ul>")
    for j in arg['mediocampistas']:
        c.append(f"<li>{e(j)}</li>")
    c.append("</ul>")
    c.append("<h4>DELANTEROS (6)</h4><ul>")
    for j in arg['delanteros']:
        c.append(f"<li>{e(j)}</li>")
    c.append("</ul>")
    c.append("<h3>BAJAS</h3><ul>")
    for b in arg['bajas']:
        c.append(f"<li>{e(b)}</li>")
    c.append("</ul>")
    c.append("<h3>NOVEDADES Y ACTUALIZACIONES</h3><ul>")
    for n in arg['novedades']:
        c.append(f"<li>{e(n)}</li>")
    c.append("</ul>")
    return bloque("SELECCION ARGENTINA", "\n".join(c))


def generar_noticias(noticias):
    c = []
    c.append("<h2>NOTICIAS ARGENTINA (FUENTES RSS LOCALES)</h2>")
    if not noticias:
        c.append("<p>NO SE PUDIERON OBTENER NOTICIAS EN ESTE MOMENTO.</p>")
        c.append("<p>EL FEED RSS UNIFICADO PUEDE ESTAR TEMPORALMENTE INACCESIBLE.</p>")
        c.append("<p>MEDIOS LOCALES MONITOREADOS: OLE.COM.AR | CLARIN.COM | LA NACION | INFOBAE | TYC SPORTS</p>")
    else:
        c.append(f"<p>TOTAL DE NOTICIAS OBTENIDAS: {len(noticias)}</p>")
        for i, n in enumerate(noticias, 1):
            c.append(f"<h3>{i}. {e(n['titulo'])}</h3>")
            if n['fecha']:
                c.append(f"<p><strong>FECHA:</strong> {e(n['fecha'])}</p>")
            c.append(f"<p><strong>FUENTE:</strong> {e(n['fuente'])}</p>")
            if n['descripcion']:
                c.append(f"<p>{e(n['descripcion'])}</p>")
    c.append("<p><em>FUENTES RSS CONSOLIDADAS: GOOGLE NEWS AR (FILTRADO POR MEDIOS LOCALES)</em></p>")
    return bloque("NOTICIAS ARGENTINA", "\n".join(c))


def generar_telecentro():
    c = []
    c.append("<h2>TRANSMISIONES TELECENTRO PLAY - MUNDIAL FIFA 2026</h2>")
    c.append("<p><strong>CANALES DISPONIBLES:</strong></p><ul>")
    c.append("<li>TELEFE: CANAL 12 (SD) / CANAL 1001 (HD)</li>")
    c.append("<li>TYC SPORTS: CANAL 106 (SD) / CANAL 1018 (HD)</li>")
    c.append("<li>TV PUBLICA: CANAL 8 (SD) / CANAL 999 (HD)</li>")
    c.append("<li>DISNEY+ PREMIUM: SERVICIO ADICIONAL (SVA) - $23.999 ARS/MES</li>")
    c.append("</ul>")
    c.append("<p><strong>LOS PARTIDOS DE ARGENTINA ESTAN MARCADOS CON [*** ARG ***]</strong></p>")
    fecha_ant = None
    for p in GRILLA_TELECENTRO:
        if p['fecha'] != fecha_ant:
            if fecha_ant is not None:
                c.append("</ul>")
            fecha_ant = p['fecha']
            c.append(f"<h3>{e(p['dia'])} {e(p['fecha'])}/2026</h3><ul>")
        arg_tag = " [*** ARG ***]" if p.get('argentina') else ""
        sva_tag = f" | SVA: {e(p['sva'])}" if p['sva'] else ""
        c.append(f"<li>{e(p['hora'])} | {e(p['partido'])}{e(arg_tag)} | {e(p['canales'])}{sva_tag}</li>")
    c.append("</ul>")
    c.append("<p><em>NOTA: PARA CONTRATAR DISNEY+ PREMIUM INGRESAR EN TELECENTRO.COM.AR O DESDE LA APP TELECENTRO PLAY.</em></p>")
    return bloque("TRANSMISIONES TELECENTRO PLAY", "\n".join(c))


def generar_faq():
    c = []
    c.append("<h2>PREGUNTAS FRECUENTES (FAQ)</h2>")
    c.append("<p>BASE DE RESPUESTAS PARA ASISTENTE VIRTUAL - TELECENTRO</p>")
    for i, (pregunta, respuesta) in enumerate(FAQ, 1):
        c.append(f"<h3>P{i}: {e(pregunta)}</h3>")
        c.append(f"<p><strong>R:</strong> {e(respuesta)}</p>")
    return bloque("FAQ", "\n".join(c))


# ============================================================
# FUNCION PRINCIPAL
# ============================================================
def generar_html():
    ahora = datetime.datetime.now()
    fecha_hoy = ahora.date()
    hora_actual = ahora.time()
    timestamp = ahora.strftime("%d/%m/%Y %H:%M:%S")

    print(f"[INFO] Iniciando generacion de mundial.html")
    print(f"[INFO] Fecha/hora: {timestamp} ARG")

    print("[INFO] Obteniendo noticias via RSS unificado...")
    noticias = obtener_noticias_rss()
    print(f"[INFO] Total noticias obtenidas: {len(noticias)}")

    partes = []
    partes.append(f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>MUNDIAL FIFA 2026 - BASE DE CONOCIMIENTO</title>
</head>
<body>

<h1>MUNDIAL FIFA 2026 - BASE DE CONOCIMIENTO</h1>
<p><strong>ULTIMA ACTUALIZACION: {e(timestamp)} (HORA ARGENTINA)</strong></p>
<p>DOCUMENTO DE CONOCIMIENTO PARA ASISTENTE VIRTUAL - TELECENTRO PLAY</p>
<hr>
""")

    partes.append(generar_estado_torneo())
    partes.append("<hr>")
    partes.append(generar_partidos_hoy(fecha_hoy))
    partes.append("<hr>")
    partes.append(generar_en_vivo(fecha_hoy, hora_actual))
    partes.append("<hr>")
    partes.append(generar_proximos_partidos(fecha_hoy))
    partes.append("<hr>")
    partes.append(generar_ultimos_resultados())
    partes.append("<hr>")
    partes.append(generar_grupos())
    partes.append("<hr>")
    partes.append(generar_llave_eliminatoria())
    partes.append("<hr>")
    partes.append(generar_goleadores())
    partes.append("<hr>")
    partes.append(generar_valla())
    partes.append("<hr>")
    partes.append(generar_tarjetas_amarillas())
    partes.append("<hr>")
    partes.append(generar_tarjetas_rojas())
    partes.append("<hr>")
    partes.append(generar_jugadores_suspendidos())
    partes.append("<hr>")
    partes.append(generar_seleccion_argentina())
    partes.append("<hr>")
    partes.append(generar_noticias(noticias))
    partes.append("<hr>")
    partes.append(generar_telecentro())
    partes.append("<hr>")
    partes.append(generar_faq())
    partes.append(f"""
<hr>
<p><em>FIN DEL DOCUMENTO - MUNDIAL FIFA 2026 BASE DE CONOCIMIENTO</em></p>
<p><em>GENERADO: {e(timestamp)} ARG</em></p>
<p><em>PROXIMA ACTUALIZACION: AUTOMATICA HORARIA (GITHUB ACTIONS CRON)</em></p>
</body>
</html>
""")

    html_content = "\n".join(partes)
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Archivo generado con éxito en ruta relativa: {ARCHIVO_SALIDA}")
    print(f"[OK] Tamanio: {len(html_content):,} bytes / {len(html_content.splitlines())} lineas")
    return True


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    try:
        generar_html()
        print("\n[LISTO] mundial.html generado correctamente.")
    except Exception as ex:
        print(f"\n[ERROR CRITICO] {ex}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
