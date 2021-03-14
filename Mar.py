from ask_sdk_core.skill_builder import SkillBuilder, CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name, get_slot_value
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response, Intent
from ask_sdk_model.ui import SimpleCard, AskForPermissionsConsentCard
from ask_sdk_model.dialog import ElicitSlotDirective
from airtable import Airtable
import os
import boto3
from pycep_correios import get_address_from_cep, WebService
from datetime import datetime, date
from random import randint
import json
import requests


key = 'keyda2y1mcH9pIIOS'
now = datetime.now()
hora = now.hour
minuto = now.minute
Lugar = 'Lugar'
Altura = 'Altura'
Data = 'Data'

airtable = Airtable('appEweMKxNAHOHyTj', 'Imported table', key)
data_atual = date.today()


sb = SkillBuilder()

# LaunchRequest é a intenção pra iniciar a Skill
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type('LaunchRequest')(handler_input)
        

    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        # Device_id é pra pegar o ID do Dispositivo Alexa do Usuário.
        access_token = handler_input.request_envelope.context.system.api_access_token
        # Access_Token é o Token necessário para fazer a Authorization.
        horaInicial = []
        dadosAlturaHora = []
        launchAltura = []
        altaTempo = []
        alturaBaixa = []
        baixaTempo = []
        alta = []
        launchHora = []

        headers = {
            "Accept": "application/json",
            "Authorization" : "Bearer " + access_token
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        # Busca o CEP do usuário
        permissao = ['read::alexa:device:all:address:country_and_postal_code'] # Permissão necessária para buscar o CEP do usuário.
    


        if cep.status_code == 403:
            resposta = 'Ative a permissão para poder utilizar a Skill!'

            handler_input.response_builder.speak(resposta).set_card(
                SimpleCard('Permissão negada!', resposta)).set_should_end_session(
                True)
            return handler_input.response_builder.response

        elif cep.status_code == 200:
            cep_dict = cep.json()
            codigoPostal = cep_dict['postalCode']
            # codigoPostal é a variável após receber o número de CEP do usuário, ex: 00000-000.
            address = get_address_from_cep(f'{codigoPostal}', webservice=WebService.APICEP)
            cidade = address['cidade']
            # cidade é a variável que realmente tem o nome da cidade do mesmo.
            cidade = cidade.lower()
            if cidade == 'salvador':
                cidade = 'bahia'


            filtro = airtable.get_all(formula=f"AND(FIND('{cidade}', {Lugar}), FIND('{data_atual}', {Data}))=1")
            # filtro é a variável que vai pegar as informações da cidade. A busca acima está buscando pela cidade do usuário e o dia atual.

            for n, c in enumerate(filtro):
                dadosAlturaHora.append(filtro[n]['fields'])

            for v, c in enumerate(dadosAlturaHora):
                launchAltura.append(dadosAlturaHora[v]['Altura'])
                # Recebe a altura dos horários de determinado dia
                launchHora.append(dadosAlturaHora[v]['Hora'])
                # Recebe o horário das marés de determinado dia.

            if len(filtro) == 0:
                # Se não tiver informação da cidade do usuário.
                respostaFinal = f'Bem-vindo a Skill de marés brasileiras! Não encontramos informações da cidade de {cidade}, mas temos informações das cidades de: Maceió, Recife, Fortaleza, João Pessoa e Salvador. Qual cidade você deseja saber?'
                handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
                    SimpleCard('Cidade não encontrada', respostaFinal)).set_should_end_session(
                    False)

                return handler_input.response_builder.response

            for c in launchHora:
                hour, minute = c.split(':')
                horaInicial.append(hour)

            for n, c in enumerate(launchAltura):
                # Pegar a altura < 1m
                if float(c) > 1.0:
                    alta.append(c)
                    altaTempo.append(launchHora[n])

                # Pegar a altura > 1m
                elif float(c) < 1.0:
                    alturaBaixa.append(c)
                    baixaTempo.append(launchHora[n])

            if cidade == 'bahia':
                cidade = 'salvador'
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

            handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
                SimpleCard('Início', respostaFinal)).set_should_end_session(
                False)

            # OBS: Toda vez que for usada a função

            return handler_input.response_builder.response

        else:
            speak_output = 'OK'
            cep_dict = cep.json()

            handler_input.response_builder.speak(speak_output).set_card(
                AskForPermissionsConsentCard(permissions=permissao)).set_should_end_session(
                False)
            # AskForPermissonsConsentCard é necessário para liberar a permissão de usar o CEP do mesmo


        return handler_input.response_builder.response

# Intenção é usada caso o usuário queira continuar sabendo informação.
class ContinuarIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('ContinuarIntent')(handler_input)

    def handle(self, handler_input):
        resposta = 'Você deseja saber o nível da maré de qual dia?'

        handler_input.response_builder.speak(resposta).ask(resposta).set_card(
            SimpleCard('Cidade e dia informado', resposta)).set_should_end_session(
            False)

        return handler_input.response_builder.response

# Intenção usada para caso o usuário não queira mais usar a skill
class NaoQueroIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('NaoQueroIntent')(handler_input)

    def handle(self, handler_input):
        numAleatorio = randint(0, 3)
        aleatorio = ['Tudo bem. Até mais.', 'Lembre-se que eu conheço os níveis das marés das cidades de Maceió, Recife, Salvador, João Pessoa e Fortaleza. Da próxima vez pode me perguntar qual o nível da maré em alguma dessas cidades que poderei te ajudar. Até a próxima.', 'Sempre que precisar de informações de marés pode me chamar!', 'Da próxima vez você pode me perguntar especificamente o horário que a maré estará alta ou baixa em uma data específica, também saberei te responder. Até mais']
        respostaFinal = aleatorio[numAleatorio]

        handler_input.response_builder.speak(respostaFinal).set_card(
            SimpleCard('Fim', respostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response




# Se o usuário optar por outra cidade, no mesmo dia
class CidadeUsuarioIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('CidadeUsuarioIntent')(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        # Pegar todos os Slots que forem usado nessa determinada intenção
        cidadeSlot = slots["City"].value
        # Pegar o slot com o nome "City"
        cidadeUsuarioHora = []
        altura = []
        dadosAlturaHora = []
        cidadeUsuarioAltura = []
        horaInicial = []
        baixaTempo = []
        alturaBaixa = []
        altaTempo = []
        alta = []
        valores = []
        if cidadeSlot == 'salvador':
            cidadeSlot = 'bahia'

        filtro = airtable.get_all(formula=f"AND(FIND('{cidadeSlot}', {Lugar}), FIND('{data_atual}', {Data}))=1")

        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])


        for v, c in enumerate(dadosAlturaHora):
            cidadeUsuarioAltura.append(dadosAlturaHora[v]['Altura'])
            cidadeUsuarioHora.append(dadosAlturaHora[v]['Hora'])


        if len(filtro) == 0:
            respostaFinal = f'Não foi encontrada nenhuma informação da cidade de {cidadeSlot}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'
            handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
                SimpleCard('Cidade não encontrada', respostaFinal)).set_should_end_session(
                False)

            return handler_input.response_builder.response


        for c in cidadeUsuarioHora:
            hour, minute = c.split(':')
            horaInicial.append(hour)

        for n, c in enumerate(cidadeUsuarioAltura):
            if float(c) > 1.0:
                alta.append(c)
                altaTempo.append(cidadeUsuarioHora[n])

            elif float(c) < 1.0:
                alturaBaixa.append(c)
                baixaTempo.append(cidadeUsuarioHora[n])

        if cidadeSlot == 'bahia':
            cidadeSlot = 'salvador'
        qntLen = len(alta)
        if len(altaTempo) == 2:
            altaResposta = f'As marés estarão altas às: {altaTempo[0]} e {altaTempo[1]}, '
        elif len(altaTempo) == 1:
            altaResposta = f'A maré estará alta às: {altaTempo[0]}, '

        if len(baixaTempo) == 2:
            baixaResposta = f'e estarão baixas às: {baixaTempo[0]} e {baixaTempo[1]}.'
        elif len(baixaTempo) == 1:
            baixaResposta = f'e estará baixa às: {baixaTempo[0]}.'

        respostaFinal = altaResposta + baixaResposta

        respostaFinal = f'Em {cidadeSlot}, {altaResposta}{baixaResposta} Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero". '


        handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).ask(respostaFinal).set_card(
            SimpleCard('Outra opção', respostaFinal)).set_should_end_session(
            False)

        return handler_input.response_builder.response


# Quando o usuário diz a cidade e o dia que ele quer saber.
class CidadeDiaIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('CidadeDiaIntent')(handler_input)


    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        diaSlot = slots['Dia'].value
        cidadeSlot = slots["Cidade"].value

        cidadeDiaAltura = []
        dadosAlturaHora = []
        altura = []
        alta = []
        alturaBaixa = []
        altaTempo = []
        baixaTempo = []
        cidadeDiaHora = []
        cidadeDiaAltura = []
        if cidadeSlot == 'salvador':
            cidadeSlot = 'bahia'

        filtro = airtable.get_all(formula=f"AND(FIND('{cidadeSlot}', {Lugar}), FIND('{diaSlot}', {Data}))=1")

        

        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])

        for v, c in enumerate(dadosAlturaHora):
            cidadeDiaAltura.append(dadosAlturaHora[v]['Altura'])
            cidadeDiaHora.append(dadosAlturaHora[v]['Hora'])

        if len(filtro) == 0:
            respostaFinal = f'Não foi encontrada nenhuma informação da cidade de {cidadeSlot}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'
            handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
                SimpleCard('Cidade não encontrada', respostaFinal)).set_should_end_session(
                False)

            return handler_input.response_builder.response


        for n, c in enumerate(cidadeDiaAltura):
            if float(c) > 1.0:
                alta.append(c)
                altaTempo.append(cidadeDiaHora[n])

            elif float(c) < 1.0:
                alturaBaixa.append(c)
                baixaTempo.append(cidadeDiaHora[n])


        diaUsado = diaSlot[8:10]
        qntLen = len(alta)
        if len(altaTempo) == 2:
            altaResposta = f'As marés estarão altas às: {altaTempo[0]} e {altaTempo[1]}, '
        elif len(altaTempo) == 1:
            altaResposta = f'A maré estará alta às: {altaTempo[0]}, '

        if len(baixaTempo) == 2:
            baixaResposta = f'e estarão baixas às: {baixaTempo[0]} e {baixaTempo[1]}.'
        elif len(altaTempo) == 1:
            baixaResposta = f'e estará baixa às: {baixaTempo[0]}.'


        respostaFinal = f'Em {cidadeSlot}, no dia {diaUsado}, {altaResposta}{baixaResposta} Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'

        handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
            SimpleCard('Determinado pelo Usuário', respostaFinal)).set_should_end_session(
            False)

        return handler_input.response_builder.response


# Quando o usuário quer saber informação de outro dia, da cidade do dispositivo.
class CidadeDiaAtualIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('CidadeDiaAtualIntent')(handler_input)


    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        slots = handler_input.request_envelope.request.intent.slots
        diaSlot = slots['Dia'].value

        cidadeDiaAltura = []
        dadosAlturaHora = []
        altura = []
        altaTempo = []
        alturaBaixa = []
        alta = []
        baixaTempo = []
        cidadeDiaHora = []
        cidadeDiaAltura = []
        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        permissao = ['read::alexa:device:all:address:country_and_postal_code']

        cep_dict = cep.json()
        codigoPostal = cep_dict['postalCode']
        address = get_address_from_cep(f'{codigoPostal}', webservice=WebService.APICEP)
        cidade = address['cidade']
        cidade = cidade.lower()
        if cidade == 'salvador':
            cidade = 'bahia'

        filtro = airtable.get_all(formula=f"AND(FIND('{cidade}', {Lugar}), FIND('{diaSlot}', {Data}))=1")

        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])

        for v, c in enumerate(dadosAlturaHora):
            cidadeDiaAltura.append(dadosAlturaHora[v]['Altura'])
            cidadeDiaHora.append(dadosAlturaHora[v]['Hora'])

        if len(filtro) == 0:
            respostaFinal = f'Não foi encontrada nenhuma informação da cidade de {cidade}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'
            handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
                SimpleCard('Cidade não encontrada', respostaFinal)).set_should_end_session(
                False)

            return handler_input.response_builder.response


        for n, c in enumerate(cidadeDiaAltura):
            if float(c) > 1.0:
                alta.append(c)
                altaTempo.append(cidadeDiaHora[n])

            elif float(c) < 1.0:
                alturaBaixa.append(c)
                baixaTempo.append(cidadeDiaHora[n])


        diaUsado = diaSlot[8:10]
        qntLen = len(alta)
        if len(altaTempo) == 2:
            altaResposta = f'As marés estarão altas às: {altaTempo[0]} e {altaTempo[1]}, '
        elif len(altaTempo) == 1:
            altaResposta = f'A maré estará alta às: {altaTempo[0]}, '

        if len(baixaTempo) == 2:
            baixaResposta = f'e estarão baixas às: {baixaTempo[0]} e {baixaTempo[1]}.'
        elif len(baixaTempo) == 1:
            baixaResposta = f'e estará baixa às: {baixaTempo[0]}.'

        respostaFinal = f'No dia {diaUsado}, {altaResposta}{baixaResposta} Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'

        handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
            SimpleCard('Determinado pelo Usuário', respostaFinal)).set_should_end_session(
            False)

        return handler_input.response_builder.response


# Quando o usuário quer saber informação de um determinado dia, querendo saber a determinada altura, ex: Quando a maré estará baixa no dia X.
class AltaBaixaDiaIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('AltaBaixaDiaIntent')(handler_input)


    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        slots = handler_input.request_envelope.request.intent.slots
        verAltura = slots['altura'].value
        diaSlot = slots['Dia'].value

        altaBaixaHora = []
        altaBaixaAltura = []
        dadosAlturaHora = []
        altaTempo = []
        alta = []
        alturaBaixa = []
        baixaTempo = []


        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        permissao = ['read::alexa:device:all:address:country_and_postal_code']
        cep_dict = cep.json()
        codigoPostal = cep_dict['postalCode']
        address = get_address_from_cep(f'{codigoPostal}', webservice=WebService.APICEP)
        cidade = address['cidade']
        cidade = cidade.lower()
        if cidade == 'salvador':
            cidade = 'bahia'

        filtro = airtable.get_all(formula=f"AND(FIND('{cidade}', {Lugar}), FIND('{diaSlot}', {Data}))=1")


        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])

        for v, c in enumerate(dadosAlturaHora):
            altaBaixaAltura.append(dadosAlturaHora[v]['Altura'])
            altaBaixaHora.append(dadosAlturaHora[v]['Hora'])

        if len(filtro) == 0:
            respostaFinal = f'Não foi encontrada nenhuma informação da cidade de {cidade}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'
            handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
                SimpleCard('Cidade não encontrada', respostaFinal)).set_should_end_session(
                False)

            return handler_input.response_builder.response




        for n, c in enumerate(altaBaixaAltura):
            if float(c) > 1.0:
                alta.append(c)
                altaTempo.append(altaBaixaHora[n])


            elif float(c) < 1.0:
                alturaBaixa.append(c)
                baixaTempo.append(altaBaixaHora[n])


        if verAltura in 'altaAltaAltasaltas':
            diaUsado = diaSlot[8:10]

            qntLen = len(alta)
            if len(altaTempo) == 2:
                respostaFinal = f'No dia {diaUsado}, as marés estarão altas às: {altaTempo[0]} e às {altaTempo[1]}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'
            elif len(altaTempo) == 1:
                respostaFinal = f'No dia {diaUsado}, a maré estará alta às: {altaTempo[0]}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'

        elif verAltura in 'baixasBaixaBaixasbaixa':
            diaUsado = diaSlot[8:10]

            qntLen = len(alta)
            if len(baixaTempo) == 2:
                respostaFinal = f'No dia {diaUsado}, As Marés estarão baixas às: {baixaTempo[0]} e às {baixaTempo[1]}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'
            elif len(baixaTempo) == 1:
                respostaFinal = f'No dia {diaUsado}, A maré estará baixa às: {baixaTempo[0]}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'


        handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
            SimpleCard('Dia determinado', respostaFinal)).set_should_end_session(
            False)

        return handler_input.response_builder.response


# Quando o usuário quer saber informação de um determinado dia de determinada cidade, querendo saber a determinada altura, ex: Quando a maré estará baixa no dia X.

class AltaBaixaDiaCidadeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('AltaBaixaDiaCidadeIntent')(handler_input)


    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        cidadeSlot = slots["Cidade"].value
        diaSlot = slots['Day'].value
        verAltura = slots['altura'].value


        alturaDiaCidade = []
        horaDiaCidade = []
        dadosAlturaHora = []
        altaTempo = []
        alta = []
        alturaBaixa = []
        baixaTempo = []
        if cidadeSlot == 'salvador':
            cidadeSlot = 'bahia'


        filtro = airtable.get_all(formula=f"AND(FIND('{cidadeSlot}', {Lugar}), FIND('{diaSlot}', {Data}))=1")


        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])


        for v, c in enumerate(dadosAlturaHora):
            alturaDiaCidade.append(dadosAlturaHora[v]['Altura'])
            horaDiaCidade.append(dadosAlturaHora[v]['Hora'])


        if len(filtro) == 0:
            respostaFinal = f'Não foi encontrada nenhuma informação da cidade de {cidadeSlot}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'
            handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
                SimpleCard('Cidade não encontrada', respostaFinal)).set_should_end_session(
                False)

            return handler_input.response_builder.response


        for n, c in enumerate(alturaDiaCidade):
            if float(c) > 1.0:
                alta.append(c)
                altaTempo.append(horaDiaCidade[n])

            elif float(c) < 1.0:
                alturaBaixa.append(c)
                baixaTempo.append(horaDiaCidade[n])

        if cidadeSlot == 'bahia':
            cidadeSlot = 'salvador'

        if verAltura in 'altaAltaAltasaltas':
            # se o usuário disser Alta, alta, Altas ou altas, entrará nessa condição.
            diaUsado = diaSlot[8:10]

            qntLen = len(alta)
            if len(altaTempo) == 2:
                respostaFinal = f'Em {cidadeSlot}, No dia {diaUsado}, As Marés estarão altas às: {altaTempo[0]} e às {altaTempo[1]}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'
            elif len(altaTempo) == 1:
                respostaFinal = f'Em {cidadeSlot}, No dia {diaUsado}, A maré estará alta às: {altaTempo[0]}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'

        elif verAltura in 'baixasBaixaBaixasbaixa':
            diaUsado = diaSlot[8:10]

            qntLen = len(alta)
            if len(baixaTempo) == 2:
                respostaFinal = f'Em {cidadeSlot}, No dia {diaUsado}, As Marés estarão baixas às: {baixaTempo[0]} e às {baixaTempo[1]}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'
            elif len(baixaTempo) == 1:
                respostaFinal = f'Em {cidadeSlot}, No dia {diaUsado}, A maré estará baixa às: {baixaTempo[0]}. Se quiser saber mais alguma informação, diga "Continuar". Se não quiser, diga "Não quero".'

        handler_input.response_builder.speak(respostaFinal).ask(respostaFinal).set_card(
            SimpleCard('Outra cidade, alta ou baixa', respostaFinal)).set_should_end_session(
            False)

        return handler_input.response_builder.response

# Caso o usuário não queira utilizar a skill
class NaoDesejaIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('NaoDesejaIntent')(handler_input)


    def handle(self, handler_input):
        speak_output = 'Obrigado por utilizar a Skill.'

        handler_input.response_builder.speak(speak_output).set_card(
            SimpleCard('Saída', speak_output)).set_should_end_session(
            True)

        return handler_input.response_builder.response

# Se o usuário falar "Cancelar" ou "Parar"
class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Saindo!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Encerrar", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response

# Se o usuário quiser uma ajuda.
class AjudaIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('AMAZON.HelpIntent')(handler_input)

    def handle(self, handler_input):
        speech_text = 'Para utilizar a skill, basta dizer "Como estará a maré no dia 22 de junho em Maceió". '

        handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
            SimpleCard('Ajuda', speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response


class SessionEndedRequest(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('SessionEndedRequestIntent')(handler_input)

    def handle(self, handler_input):
        speech_text = 'Saindo!'

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard('Finalizar', speech_text)).set_should_end_session(
            True)

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CidadeUsuarioIntentHandler())
sb.add_request_handler(ContinuarIntent())
sb.add_request_handler(NaoQueroIntent())
sb.add_request_handler(CidadeDiaAtualIntentHandler())
sb.add_request_handler(CidadeDiaIntentHandler())
sb.add_request_handler(AltaBaixaDiaIntentHandler())
sb.add_request_handler(AltaBaixaDiaCidadeIntentHandler())
sb.add_request_handler(NaoDesejaIntentHandler())
sb.add_request_handler(SessionEndedRequest())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(AjudaIntentHandler())
