from datetime import datetime
from airtable import Airtable
import json
import requests
from datetime import datetime, timedelta, date
import time

Lugar = 'Lugar'
Data = 'Data'
key = 'keyda2y1mcH9pIIOS'
airtable = Airtable('appEweMKxNAHOHyTj', 'Imported table', key)

"""key = 'keyda2y1mcH9pIIOS'
now = datetime.now()
hora = now.hour
minuto = now.minute
data_atual = datetime.today()


diaAnterior = 1
diaAnterior = data_atual - timedelta(days=diaAnterior)
diaAnterior = str(diaAnterior)
diaAnterior = diaAnterior[0:10]


data_atual = str(data_atual)
dataUsar = data_atual[0:10]



airtable = Airtable('appEweMKxNAHOHyTj', 'Imported table', key)
Lugar = 'Lugar'
Data = 'Data'
Altura = 'Altura'

dias30 = datetime.today() + timedelta(days=30)


horario = airtable.get_all(formula=f"AND(AND(IS_AFTER({Data}, '{diaAnterior}'), IS_BEFORE({Data}, '{dias30}')), FIND('maceió',{Lugar}))")


for n, c in enumerate(horario):
    Dados.append(horario[n]['fields'])

for n, v in enumerate(Dados):
    if Dados[n]['Data'] == dataUsar:
        dadosHora.append(Dados[n]['Hora'])
        dadosAltura.append(Dados[n]['Altura'])


hora2 = 19
hora1 = 18
v = 1

for c in dadosHora:
    horas = c[0:2]
    
    if hora1 <= int(horas) <= hora2:
        print(f'entre às {hora1} e às {hora2} terá maré às: {c}')
    else:
        while v < 31:
            Busca = datetime.today() + timedelta(days=v)
            v += 1
            Busca = str(Busca)
            Busca = Busca[0:10]
            for n, k in enumerate(Dados):
                if Dados[n]['Data'] == Busca:
                    dadosHora1.append(Dados[n]['Hora'])
                    dadosAltura1.append(Dados[n]['Altura'])

            for t, c in enumerate(dadosHora1):
                horas = c[0:2]
                if hora1 <= int(horas) <= hora2:
                    resposta = f'no dia {Busca[0:2]}, entre às {hora1} e às {hora2} a maré estará com {dadosAltura1[t]} às {c}'
                    break"""
cidadeSlot = 'são paulo'
data_atual = date.today()
filtro = airtable.get_all(formula=f"AND(FIND('{cidadeSlot}', {Lugar}), FIND('{data_atual}', {Data}))=1")
print(len(filtro))
