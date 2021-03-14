from airtable import Airtable
from datetime import date, datetime

key = 'keyda2y1mcH9pIIOS'
now = datetime.now()
hora = now.hour
minuto = now.minute
launchAltura = []
launchHora = []
dadosAlturaHora = []
horaInicial = []
altaTempo = []
alta = []
baixaTempo = []
alturaBaixa = []
cidadeVeri = ['Start']


airtable = Airtable('appEweMKxNAHOHyTj', 'Imported table', key)
data_atual = date.today()

cidade = 'salvador'
if cidade == 'salvador':
    cidade = 'bahia'

filtro = airtable.search('Data', str(data_atual))

for n, c in enumerate(filtro):
    dadosAlturaHora.append(filtro[n]['fields'])

for v, c in enumerate(dadosAlturaHora):
    if dadosAlturaHora[v]['Lugar'] == cidade:

        cidadeVeri.append(dadosAlturaHora[v]['Lugar'])
        launchAltura.append(dadosAlturaHora[v]['Altura'])
        launchHora.append(dadosAlturaHora[v]['Hora'])

if len(cidadeVeri) == 1: 
    respostaFinal = f'Bem-vindo a Skill de marés brasileiras! Não encontramos informações da cidade de {cidade}, mas temos informações das cidades de: Maceió, Recife, Fortaleza, João Pessoa e Salvador. Qual cidade você deseja saber?'
        
    print(respostaFinal)


for c in launchHora:
    hour, minute = c.split(':')
    horaInicial.append(hour)
if cidade == 'bahia':
    cidade = 'salvador'

for n, c in enumerate(launchAltura):
    if float(c) > 1.0:
        alta.append(c)
        altaTempo.append(launchHora[n])


    elif float(c) < 1.0:
        alturaBaixa.append(c)
        baixaTempo.append(launchHora[n])


qntLen = len(alta)
if len(altaTempo) == 2:
    altaResposta = f'As marés estarão altas às: {altaTempo[0]} e {altaTempo[1]}, '
elif len(altaTempo) == 1:
    altaResposta = f'A maré estará alta às: {altaTempo[0]}, '

if len(baixaTempo) == 2:
    baixaResposta = f'e estarão baixas às: {baixaTempo[0]} e {baixaTempo[1]}.'
elif len(baixaTempo) == 1:
    baixaResposta = f'e estará baixa às: {baixaTempo[0]}.'

respostaFinal = f'Bem-vindo a skill de marés brasileiras! Em {cidade}, {altaResposta}{baixaResposta} Se quiser informação de outra data, basta dizer "Continuar", caso não queira diga "Não quero". '
print(respostaFinal)