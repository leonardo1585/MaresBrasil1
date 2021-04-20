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
import json
import requests


key = 'keyda2y1mcH9pIIOS'
now = datetime.now()
hora = now.hour
minuto = now.minute


airtable = Airtable('appEweMKxNAHOHyTj', 'Imported table', key)
data_atual = date.today()


sb = SkillBuilder()


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type('LaunchRequest')(handler_input)

    
    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        horaInicial = []
        dadosAlturaHora = []
        
        headers = {
            "Authorization" : "Bearer " + access_token
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        permissao = ['read::alexa:device:all:address:country_and_postal_code']
        if cep.status_code == 200:
            cep_dict = cep.json()
            codigoPostal = cep_dict['postalCode']

            address = get_address_from_cep(f'{codigoPostal}', webservice=WebService.APICEP)
            cidade = address['cidade']
            speak_output = f'Bem-vindo a Skill de Marés Brasileiras. Você deseja ver a maré da cidade de {cidade}? Se não, diga-me o nome da cidade desejada.'

            handler_input.response_builder.speak(speak_output).ask(speak_output).set_card(
                SimpleCard('Início', speak_output)).set_should_end_session(
                False)

            return handler_input.response_builder.response

        speak_output = 'OK'
        cep_dict = cep.json()
        print(cep)

        handler_input.response_builder.speak(speak_output).set_card(
            AskForPermissionsConsentCard(permissions=permissao)).set_should_end_session(
            True)

        return handler_input.response_builder.response



# RESPOSTA PARA SE O USUÁRIO DISSER SIM
class CidadeAtualIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('CidadeAtualIntent')(handler_input)


    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        slots = handler_input.request_envelope.request.intent.slots
        

        cidadeAtualHora = []
        cidadeAtualAltura = []
        dadosAlturaHora = []
        altura = []
        horaInicial = []
        valores = []
        
        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        permissao = ['read::alexa:device:all:address:country_and_postal_code']
        
        cep_dict = cep.json()
        codigoPostal = cep_dict['postalCode']
        address = get_address_from_cep(f'{codigoPostal}', webservice=WebService.VIACEP)
        cidade = address['cidade']
        cidade = cidade.lower()

        filtro = airtable.search('Data', str(data_atual))

        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])

        for v, c in enumerate(dadosAlturaHora):
            if dadosAlturaHora[v]['Lugar'] == cidade:
                cidadeAtualAltura.append(dadosAlturaHora[v]['Altura'])
                cidadeAtualHora.append(dadosAlturaHora[v]['Hora'])

        for c in cidadeAtualHora:
            hour, minute = c.split(':')
            horaInicial.append(hour)

        for k, c in enumerate(horaInicial):
            result = horaInicial[k]
            result1 = (hora - int(result))
            
            if result1 >= 0:
                valores.append(result1)
                if result1 == min(valores):
                    valor = horaInicial[k]
                    pos = horaInicial.index(str(valor))

        if float(cidadeAtualAltura[pos]) < 1.0:
            altura = 'baixa'
        elif float(cidadeAtualAltura[pos]) >= 1.0:
            altura = 'alta'


        respostaFinal = f'Às {cidadeAtualHora[pos]}h a maré estará ou esteve com a altura de {cidadeAtualAltura[pos]}m, considerada como maré {altura}.'


        handler_input.response_builder.speak(respostaFinal).set_card(
            SimpleCard('Cidade atual', respostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response


# SE O USUÁRIO DISSER O NOME DA CIDADE
class CidadeUsuarioIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('CidadeUsuarioIntent')(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        cidadeSlot = slots["City"].value
        cidadeUsuarioHora = []
        altura = []
        dadosAlturaHora = []
        cidadeUsuarioAltura = []
        horaInicial = []
        valores = []
        cidadeVeri = ['Start']
        
        filtro = airtable.search('Data', str(data_atual))


        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])


        for v, c in enumerate(dadosAlturaHora):
            if dadosAlturaHora[v]['Lugar'] == cidadeSlot:
                cidadeVeri.append(dadosAlturaHora[v]['Lugar'])
                cidadeUsuarioAltura.append(dadosAlturaHora[v]['Altura'])
                cidadeUsuarioHora.append(dadosAlturaHora[v]['Hora'])


        if len(cidadeVeri) == 1: 
            respostaFinal = f'Não foi encontrada nenhuma informação da cidade de {cidadeSlot}.'
            handler_input.response_builder.speak(respostaFinal).set_card(
                SimpleCard('Cidade não encontrada', respostaFinal)).set_should_end_session(
                True)

            return handler_input.response_builder.response


        for c in cidadeUsuarioHora:
            hour, minute = c.split(':')
            horaInicial.append(hour)

        for k, c in enumerate(horaInicial):
            result = horaInicial[k]
            result1 = (hora - int(result))
            
            if result1 >= 0:
                valores.append(result1)
                if result1 == min(valores):
                    valor = horaInicial[k]
                    pos = horaInicial.index(str(valor))


        if float(cidadeUsuarioAltura[pos]) < 1.0:
            altura = 'baixa'
        elif float(cidadeUsuarioAltura[pos]) >= 1.0:
            altura = 'alta'

        respostaFinal = f'Às {cidadeUsuarioHora[pos]} a maré estará ou esteve com a altura de {cidadeUsuarioAltura[pos]}m, considerada como maré {altura}.'

                    
        handler_input.response_builder.speak(respostaFinal).set_card(
            SimpleCard('Outra opção', respostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response


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
        cidadeDiaHora = []
        cidadeVeri = ['Start']
        filtro = airtable.search('Data', str(data_atual))

        for v, c in enumerate(dadosAlturaHora):
            if dadosAlturaHora[v]['Lugar'] == cidadeSlot:
                cidadeVeri.append(dadosAlturaHora[v]['Lugar'])
                cidadeDiaAltura.append(dadosAlturaHora[v]['Altura'])
                cidadeDiaHora.append(dadosAlturaHora[v]['Hora'])


        if len(cidadeVeri) == 1: 
            respostaFinal = f'Não foi encontrada nenhuma informação da cidade de {cidadeSlot}.'
            handler_input.response_builder.speak(respostaFinal).set_card(
                SimpleCard('Cidade não encontrada', respostaFinal)).set_should_end_session(
                True)

            return handler_input.response_builder.response


        for c in cidadeDiaAltura:
            if float(c) < 1.0:
                altura.append('baixa')
            elif float(c) >= 1.0:
                altura.append('alta')

        
        diaUsado = diaSlot[8:10]
            
        
        respostaFinal = f'No dia {diaUsado}, Às {alturaDiaHora[1]} a maré estará {altura[1]} com {cidadeDiaAltura[1]}m de altura e às {cidadeDiaHora[2]} a maré estará {altura[2]} com {cidadeDiaAltura[2]}m de altura.'

        handler_input.response_builder.speak(respostaFinal).set_card(
            SimpleCard('Determinado pelo Usuário', respostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response



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
        address = get_address_from_cep(f'{codigoPostal}', webservice=WebService.VIACEP)
        cidade = address['cidade']
        cidade = cidade.lower()

        filtro = airtable.search('Data', str(data_atual))


        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])

        for v, c in enumerate(dadosAlturaHora):
            if dadosAlturaHora[v]['Lugar'] == cidade:
                altaBaixaAltura.append(dadosAlturaHora[v]['Altura'])
                altaBaixaHora.append(dadosAlturaHora[v]['Hora'])
                print(dadosAlturaHora[v])



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
            if qntLen == 2:
                respostaFinal = f'No dia {diaUsado}, as marés estarão altas às: {altaTempo[0]} e às {altaTempo[1]}.'
            elif qntLen == 1:
                respostaFinal = f'No dia {diaUsado}, a maré estará alta às: {altaTempo[0]}.'
        
        elif verAltura in 'baixasBaixaBaixasbaixa':
            diaUsado = diaSlot[8:10]

            qntLen = len(alta)
            if qntLen == 2:
                respostaFinal = f'No dia {diaUsado}, As Marés estarão baixas às: {alturaBaixa[0]} e às {baixaTempo[1]}.'
            elif qntLen == 1:
                respostaFinal = f'No dia {diaUsado}, A maré estará baixa às: {baixaTempo[0]}.' 

        print(respostaFinal)  

        handler_input.response_builder.speak(respostaFinal).set_card(
            AskForPermissionsConsentCard(permissions=permissao)).set_should_end_session(
            True)

        return handler_input.response_builder.response

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
        cidadeVeri = ['Start']
        
        filtro = airtable.search('Data', str(data_atual))

        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])


        for v, c in enumerate(dadosAlturaHora):
            if dadosAlturaHora[v]['Lugar'] == cidadeSlot:
                cidadeVeri.append(dadosAlturaHora[v]['Lugar'])
                alturaDiaCidade.append(dadosAlturaHora[v]['Altura'])
                horaDiaCidade.append(dadosAlturaHora[v]['Hora'])


        if len(cidadeVeri) == 1: 
            respostaFinal = f'Não foi encontrada nenhuma informação da cidade de {cidadeSlot}.'
            handler_input.response_builder.speak(respostaFinal).set_card(
                SimpleCard('Cidade não encontrada', respostaFinal)).set_should_end_session(
                True)

            return handler_input.response_builder.response


        for n, c in enumerate(alturaDiaCidade):
            if float(c) > 1.0:
                alta.append(c)
                altaTempo.append(horaDiaCidade[n])

            elif float(c) < 1.0:
                alturaBaixa.append(c)
                baixaTempo.append(horaDiaCidade[n])

        if verAltura in 'altaAltaAltasaltas':
            diaUsado = diaSlot[8:10]

            qntLen = len(alta)
            if qntLen == 2:
                respostaFinal = f'Em {cidadeSlot}, No dia {diaUsado}, As Marés estarão altas às: {altaTempo[0]} e às {altaTempo[1]}.'
            elif qntLen == 1:
                respostaFinal = f'Em {cidadeSlot}, No dia {diaUsado}, A maré estará alta às: {altaTempo[0]}.'
        
        elif verAltura in 'baixasBaixaBaixasbaixa':
            diaUsado = diaSlot[8:10]

            qntLen = len(alta)
            if qntLen == 2:
                respostaFinal = f'Em {cidadeSlot}, No dia {diaUsado}, As Marés estarão baixas às: {alturaBaixa[0]} e às {baixaTempo[1]}.'
            elif qntLen == 1:
                respostaFinal = f'Em {cidadeSlot}, No dia {diaUsado}, A maré estará baixa às: {baixaTempo[0]}.'

        handler_input.response_builder.speak(respostaFinal).set_card(
            SimpleCard('Outra cidade, alta ou baixa', respostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response


class ProximoDiaMaresIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('ProximoDiaMaresIntent')(handler_input)

    
    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        slots = handler_input.request_envelope.request.intent.slots
        diaSlot = slots['Days'].value

        proximoDiaAltura = []
        proximoDiaHora = []
        dadosAlturaHora = []
        altura = []


        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        permissao = ['read::alexa:device:all:address:country_and_postal_code']
        cep_dict = cep.json()
        codigoPostal = cep_dict['postalCode']
        address = get_address_from_cep(f'{codigoPostal}', webservice=WebService.VIACEP)
        cidade = address['cidade']
        cidade = cidade.lower()

        filtro = airtable.search('Data', str(data_atual))

        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])

        for v, c in enumerate(dadosAlturaHora):
            if dadosAlturaHora[v]['Lugar'] == cidade:
                proximoDiaAltura.append(dadosAlturaHora[v]['Altura'])
                proximoDiaHora.append(dadosAlturaHora[v]['Hora'])
                print(dadosAlturaHora[v])


        for c in proximoDiaAltura:
            if float(c) < 1.0:
                altura.append('baixa')
            elif float(c) >= 1.0:
                altura.append('alta')

        
        diaUsado = diaSlot[8:10]

        respostaFinal = f'Amanhã, Às {proximoDiaHora[1]} a maré estará {altura[1]} com {proximoDiaAltura[1]}m de altura e às {proximoDiaHora[2]} a maré estará {altura[2]} com {proximoDiaAltura[2]}m de altura.'

        handler_input.response_builder.speak(respostaFinal).set_card(
            AskForPermissionsConsentCard(permissions=permissao)).set_should_end_session(
            True)

        return handler_input.response_builder.response


class ProximoDiaCidadeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('ProximoDiaCidadeIntent')(handler_input)

    
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        diaSlot = slots['Days'].value
        cidadeSlot = slots['Cidade'].value

        proximodiaAltura = []
        dadosAlturaHora = []
        proximoDiaHora = []
        altura = []

        filtro = airtable.search('Data', str(data_atual))


        for n, c in enumerate(filtro):
            dadosAlturaHora.append(filtro[n]['fields'])

        for v, c in enumerate(dadosAlturaHora):
            if dadosAlturaHora[v]['Lugar'] == cidadeSlot:
                cidadeAtualAltura.append(dadosAlturaHora[v]['Altura'])
                cidadeAtualHora.append(dadosAlturaHora[v]['Hora'])
                print(dadosAlturaHora[v])


        for c in proximodiaAltura:
            if float(c) < 1.0:
                altura.append('baixa')
            elif float(c) >= 1.0:
                altura.append('alta')

        
        diaUsado = diaSlot[8:10]

        respostaFinal = f'Amanhã, Às {proximoDiaHora[1]} a maré estará {altura[1]} com {proximoDiaAltura[1]}m de altura e às {proximoDiaHora[2]} a maré estará {altura[2]} com {proximoDiaAltura[2]}m de altura.'

        handler_input.response_builder.speak(respostaFinal).set_card(
            SimpleCard('Próximo dia', respostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response    


class NaoDesejaIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('NaoDesejaIntent')(handler_input)


    def handle(self, handler_input):
        speak_output = 'Ok. Obrigado por utilizar a Skill.'

        handler_input.response_builder.speak(speak_output).set_card(
            SimpleCard('Saída', speak_output)).set_should_end_session(
            True)

        return handler_input.response_builder.response


class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response



sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CidadeAtualIntentHandler())
sb.add_request_handler(CidadeUsuarioIntentHandler())
sb.add_request_handler(CidadeDiaIntentHandler())
sb.add_request_handler(AltaBaixaDiaIntentHandler())
sb.add_request_handler(AltaBaixaDiaCidadeIntentHandler())
sb.add_request_handler(ProximoDiaMaresIntentHandler())
sb.add_request_handler(ProximoDiaCidadeIntentHandler())
sb.add_request_handler(NaoDesejaIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
