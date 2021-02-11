from datetime import datetime
from airtable import Airtable
import json
import requests
from datetime import date
import time


data_atual = date.today()
key = 'keyda2y1mcH9pIIOS'
airtable = Airtable('appEweMKxNAHOHyTj', 'Table 1', key)
filtro = airtable.search('Lugar', 'Maceió')
now = datetime.now()
hora = now.hour
minuto = now.minute
RespostaFinal = fight = ''



total = []
lista = []
resultado = []
teste = []
Ni = []
alt = []
tempo = []
altura = []
cont = 0
filtro = airtable.search('Lugar', 'maceió')
for n, c in enumerate(filtro):
    lista.append(filtro[n]['fields'])


for v, c in enumerate(lista):
    if lista[v]['Data'] == str(data_atual):
        teste.append(lista[v]['Altura'])
        resultado.append(lista[v]['Hora'])

for n, c in enumerate(teste):
    if float(c) < 1.0:
        alt.append(c)
        tempo.append(resultado[n])

qnt = len(alt)
if qnt == 2:
    RespostaFinal = f'As Marés estarão baixas às: {tempo[0]} e às {tempo[1]}'
elif qnt == 1:
    RespostaFinal = f'A maré estará baixa às: {tempo[0]}'

print(RespostaFinal)

