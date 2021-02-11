from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name, get_slot_value
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response, Intent
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.dialog import ElicitSlotDirective
from airtable import Airtable
from pycep_correios import get_address_from_cep, WebService
from datetime import datetime, date
import json
import requests


key = 'keyda2y1mcH9pIIOS'
now = datetime.now()
hora = now.hour
minuto = now.minute
RespostaFinal = ''


airtable = Airtable('appEweMKxNAHOHyTj', 'Table 1', key)
data_atual = date.today()


sb = SkillBuilder()


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type('LaunchRequest')(handler_input)

    
    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        Ni = []
        lista = []
        fight = ''
        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        TimeZone = requests.get(f'https://api.amazonalexa.com/v2/devices/{device_id}/settings/System.timeZone', headers=headers)
        time = TimeZone.json()
        cep_dict = cep.json()
        cep_real = cep_dict['postalCode']

        address = get_address_from_cep(f'{cep_real}', webservice=WebService.VIACEP)
        cidade = address['cidade']
        speak_output = f'Bem-vindo a Skill de Marés Brasileiras. Você deseja ver a maré da cidade de {cidade}? Se não, diga-me o nome da cidade desejada.'
        
        handler_input.response_builder.speak(speak_output).ask(speak_output).set_card(
            SimpleCard('Início', speak_output)).set_should_end_session(
            False)

        return handler_input.response_builder.response


# RESPOSTA PARA SE O USUÁRIO DISSER SIM
class OpcaoUmIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('OpcaoUmIntent')(handler_input)


    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        slots = handler_input.request_envelope.request.intent.slots
        opc1 = []
        opc11 = []
        tempo = []
        lista = []
        altura = []
        Ni = []
        
        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        cep_dict = cep.json()
        cep_real = cep_dict['postalCode']
        address = get_address_from_cep(f'{cep_real}', webservice=WebService.VIACEP)
        cidade = address['cidade']
        cidade = cidade.lower()
        airtable = Airtable('appEweMKxNAHOHyTj', 'Table 1', key)
        filtro = airtable.search('Lugar', cidade)
        for n, c in enumerate(filtro):
            lista.append(filtro[n]['fields'])


        for v, c in enumerate(lista):
            if lista[v]['Data'] == str(data_atual):
                opc11.append(lista[v]['Altura'])
                opc1.append(lista[v]['Hora'])

        for c in opc1:
            hour, minute = c.split(':')
            Ni.append(hour)

        for k, c in enumerate(Ni):
            result = Ni[k]
            result1 = (hora - int(result))
            if result1 >= 0:
                final = result1 - hora
                fight = Ni[k]
                pos = Ni.index(str(fight))
            else:
                RespostaFinal = ''
        if float(opc11[pos]) < 1.0:
            consid = 'baixa'
        elif float(opc11[pos]) >= 1.0:
            consid = 'alta'

        if consid == 'alta':
            consid2 = 'baixa'
        elif consid == 'baixa':
            consid2 = 'alta'
        RespostaFinal = f'Às {opc1[pos]}h a maré estará ou esteve com a altura de {opc11[pos]}m, considerada como maré {consid}.'
        print(opc1[pos])
        print(opc11[pos])

        handler_input.response_builder.speak(RespostaFinal).set_card(
            SimpleCard("Altura atual", RespostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response


# SE O USUÁRIO DISSER O NOME DA CIDADE
class OpcaoDoisIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('OpcaoDoisIntent')(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        nome = slots["City"].value
        airtable = Airtable('appEweMKxNAHOHyTj', 'Table 1', key)
        
        filtro = airtable.search('Lugar', nome)
        if len(filtro) == 0:
            RespostaFinal = f'Não foi encontrada nenhuma informação da cidade de {nome}.'
            handler_input.response_builder.speak(RespostaFinal).set_card(
                SimpleCard('Cidade não encontrada', RespostaFinal)).set_should_end_session(
                True)

            return handler_input.response_builder.response

        opc2 = []
        tempo = []
        fight1 = ''
        altura = []
        lista = []
        opc22 = []
        Ni = []
        for n, c in enumerate(filtro):
            lista.append(filtro[n]['fields'])


        for v, c in enumerate(lista):
            if lista[v]['Data'] == str(data_atual):
                opc22.append(lista[v]['Altura'])
                opc2.append(lista[v]['Hora'])


        for c in opc2:
            hour, minute = c.split(':')
            Ni.append(hour)


        for k, c in enumerate(Ni):
            result = Ni[k]
            result1 = (hora - int(result))
            if result1 >= 0:
                final = result1 - hora
                fight1 = Ni[k]
                pos = Ni.index(str(fight1))
            else:
                RespostaFinal = ''


        if float(opc22[pos]) < 1.0:
            consid = 'baixa'
        elif float(opc22[pos]) >= 1.0:
            consid = 'alta'

        if consid == 'alta':
            consid2 = 'baixa'
        elif consid == 'baixa':
            consid2 = 'alta'

        RespostaFinal = f'Às {opc2[pos]} a maré estará ou esteve com a altura de {opc22[pos]}m, considerada como maré {consid}.'
        print(opc2[pos])
        print(opc22[pos])
                    
        handler_input.response_builder.speak(RespostaFinal).set_card(
            SimpleCard('Outra opção', RespostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response


class OpcaoTresIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('OpcaoTresIntent')(handler_input)

    
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        data = []
        opc3 = []
        lista = []
        altura = []
        tempo = []
        opc33 = []
        Ni = []
        dia = slots['Dia'].value
        nome = slots["Cidade"].value

        filtro = airtable.search('Lugar', nome)
        if len(filtro) == 0:
            RespostaFinal = f'Não foi encontrada nenhuma informação da cidade de {nome}.'
            handler_input.response_builder.speak(RespostaFinal).set_card(
                SimpleCard('Cidade não encontrada', RespostaFinal)).set_should_end_session(
                True)

            return handler_input.response_builder.response


        for n, c in enumerate(filtro):
            lista.append(filtro[n]['fields'])


        for v, c in enumerate(lista):
            if lista[v]['Data'] == str(dia):
                opc3.append(lista[v]['Altura'])
                opc33.append(lista[v]['Hora'])


        for c in opc3:
            if float(c) < 1.0:
                altura.append('baixa')
            elif float(c) >= 1.0:
                altura.append('alta')

        
        data.append(dia[8])
        data.append(dia[9])
        values = ''.join(str(t) for t in data)
            
        
        RespostaFinal = f'No dia {values}, Às {opc33[1]} a maré estará {altura[1]} com {opc3[1]}m de altura e às {opc33[2]} a maré estará {altura[2]} com {opc3[2]}m de altura.'

        handler_input.response_builder.speak(RespostaFinal).set_card(
            SimpleCard('Determinado pelo Usuário', RespostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response


class OpcaoQuatroIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('OpcaoQuatroIntent')(handler_input)

    
    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        slots = handler_input.request_envelope.request.intent.slots
        day = []
        opc4 = []
        alt = []
        altura = []
        lista = []
        tempo = []
        opc44 = []
        Ni = []
        dia = slots['Dia'].value
        RespostaFinal = ''
        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        cep_dict = cep.json()
        cep_real = cep_dict['postalCode']
        address = get_address_from_cep(f'{cep_real}', webservice=WebService.VIACEP)
        cidade = address['cidade']
        cidade = cidade.lower()
        airtable = Airtable('appEweMKxNAHOHyTj', 'Table 1', key)
        filtro = airtable.search('Lugar', cidade)
        for n, c in enumerate(filtro):
            lista.append(filtro[n]['fields'])


        for v, c in enumerate(lista):
            if lista[v]['Data'] == str(dia):
                opc4.append(lista[v]['Altura'])
                opc44.append(lista[v]['Hora'])

        for n, c in enumerate(opc4):
            if float(c) < 1.0:
                alt.append(c)
                tempo.append(opc44[n])

        day.append(dia[8])
        day.append(dia[9])
        values = ''.join(str(t) for t in day)

        qnt = len(alt)
        if qnt == 2:
            RespostaFinal = f'No dia {values}, As Marés estarão baixas às: {tempo[0]} e às {tempo[1]}.'
        elif qnt == 1:
            RespostaFinal = f'No dia {values}, A maré estará baixa às: {tempo[0]}.'


        handler_input.response_builder.speak(RespostaFinal).set_card(
            SimpleCard('Maré(s) baixa(s)', RespostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response


class OpcaoCincoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('OpcaoCincoIntent')(handler_input)

    
    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        slots = handler_input.request_envelope.request.intent.slots
        day = []
        opc5 = []
        altura = []
        lista = []
        alt = []
        tempo = []
        Ni = []
        opc55 = []
        RespostaFinal = ''
        dia = slots['Dia'].value
        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        cep_dict = cep.json()
        cep_real = cep_dict['postalCode']
        address = get_address_from_cep(f'{cep_real}', webservice=WebService.VIACEP)
        cidade = address['cidade']
        cidade = cidade.lower()
        airtable = Airtable('appEweMKxNAHOHyTj', 'Table 1', key)
        filtro = airtable.search('Lugar', cidade)
        for n, c in enumerate(filtro):
            lista.append(filtro[n]['fields'])


        for v, c in enumerate(lista):
            if lista[v]['Data'] == str(dia):
                opc5.append(lista[v]['Altura'])
                opc55.append(lista[v]['Hora'])

        for n, c in enumerate(opc5):
            if float(c) > 1.0:
                alt.append(c)
                tempo.append(opc55[n])

        day.append(dia[8])
        day.append(dia[9])
        values = ''.join(str(t) for t in day)

        qnt = len(alt)
        if qnt == 2:
            RespostaFinal = f'No dia {values}, As Marés estarão altas às: {tempo[0]} e às {tempo[1]}.'
        elif qnt == 1:
            RespostaFinal = f'No dia {values}, A maré estará alta às: {tempo[0]}.'


        handler_input.response_builder.speak(RespostaFinal).set_card(
            SimpleCard('Maré(s) baixa(s)', RespostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response    


class OpcaoSeisIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('OpcaoSeisIntent')(handler_input)


    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        nome = slots["Cidade"].value
        dia = slots['Day'].value
        day = []
        opc6 = []
        opc66 = []
        lista = []
        Ni = []
        tempo = []
        alt = []
        altura = []
        RespostaFinal = ''
        airtable = Airtable('appEweMKxNAHOHyTj', 'Table 1', key)
        filtro = airtable.search('Lugar', nome)
        if len(filtro) == 0:
            RespostaFinal = f'Não foi encontrada nenhuma informação da cidade de {nome}.'
            handler_input.response_builder.speak(RespostaFinal).set_card(
                SimpleCard('Cidade não encontrada', RespostaFinal)).set_should_end_session(
                True)

            return handler_input.response_builder.response
        for n, c in enumerate(filtro):
            lista.append(filtro[n]['fields'])


        for v, c in enumerate(lista):
            if lista[v]['Data'] == str(dia):
                opc6.append(lista[v]['Altura'])
                opc66.append(lista[v]['Hora'])


        for n, c in enumerate(opc6):
            if float(c) > 1.0:
                alt.append(c)
                tempo.append(opc66[n])

        day.append(dia[8])
        day.append(dia[9])
        values = ''.join(str(t) for t in day)

        qnt = len(alt)
        if qnt == 2:
            RespostaFinal = f'Em {nome}, No dia {values}, As Marés estarão altas às: {tempo[0]} e às {tempo[1]}.'
        elif qnt == 1:
            RespostaFinal = f'Em {nome}, No dia {values}, A maré estará alta às: {tempo[0]}.'

        handler_input.response_builder.speak(RespostaFinal).set_card(
            SimpleCard('Outra cidade, alta', RespostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response


class OpcaoSeteIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('OpcaoSeteIntent')(handler_input)


    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        nome = slots["Cidadez"].value
        dia = slots['Days'].value
        day = []
        opc7 = []
        tempo = []
        lista = []
        opc77 = []
        Ni = []
        alt = []
        altura = []
        RespostaFinal = ''
        airtable = Airtable('appEweMKxNAHOHyTj', 'Table 1', key)
        filtro = airtable.search('Lugar', nome)
        if len(filtro) == 0:
            RespostaFinal = f'Não foi encontrada nenhuma informação da cidade de {nome}.'
            handler_input.response_builder.speak(RespostaFinal).set_card(
                SimpleCard('Cidade não encontrada', RespostaFinal)).set_should_end_session(
                True)

            return handler_input.response_builder.response
        for n, c in enumerate(filtro):
            lista.append(filtro[n]['fields'])


        for v, c in enumerate(lista):
            if lista[v]['Data'] == str(dia):
                opc7.append(lista[v]['Altura'])
                opc77.append(lista[v]['Hora'])


        for n, c in enumerate(opc7):
            if float(c) < 1.0:
                alt.append(c)
                tempo.append(opc77[n])

        day.append(dia[8])
        day.append(dia[9])
        values = ''.join(str(t) for t in day)

        qnt = len(alt)
        if qnt == 2:
            RespostaFinal = f'Em {nome}, No dia {values}, As Marés estarão baixas às: {tempo[0]} e às {tempo[1]}.'
        elif qnt == 1:
            RespostaFinal = f'Em {nome}, No dia {values}, A maré estará baixa às: {tempo[0]}.'

        handler_input.response_builder.speak(RespostaFinal).set_card(
            SimpleCard('Outra cidade, baixa', RespostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response        


class OpcaoOitoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('OpcaoOitoIntent')(handler_input)

    
    def handle(self, handler_input):
        device_id = handler_input.request_envelope.context.system.device.device_id
        access_token = handler_input.request_envelope.context.system.api_access_token
        slots = handler_input.request_envelope.request.intent.slots
        dia = slots['Days'].value
        day = []
        opc8 = []
        tempo = []
        lista = []
        opc88 = []
        data = []
        Ni = []
        alt = []
        altura = []
        headers = {
            "Authorization" : f"Bearer {access_token}"
        }
        cep = requests.get(f"https://api.amazonalexa.com/v1/devices/{device_id}/settings/address/countryAndPostalCode", headers=headers)
        cep_dict = cep.json()
        cep_real = cep_dict['postalCode']
        address = get_address_from_cep(f'{cep_real}', webservice=WebService.VIACEP)
        cidade = address['cidade']
        cidade = cidade.lower()

        filtro = airtable.search('Lugar', cidade)

        for n, c in enumerate(filtro):
            lista.append(filtro[n]['fields'])


        for v, c in enumerate(lista):
            if lista[v]['Data'] == str(dia):
                opc8.append(lista[v]['Altura'])
                opc88.append(lista[v]['Hora'])


        for c in opc8:
            if float(c) < 1.0:
                altura.append('baixa')
            elif float(c) >= 1.0:
                altura.append('alta')

        
        data.append(dia[8])
        data.append(dia[9])
        values = ''.join(str(t) for t in data)

        RespostaFinal = f'Amanhã, Às {opc88[1]} a maré estará {altura[1]} com {opc8[1]}m de altura e às {opc88[2]} a maré estará {altura[2]} com {opc8[2]}m de altura.'

        handler_input.response_builder.speak(RespostaFinal).set_card(
            SimpleCard('Próximo dia', RespostaFinal)).set_should_end_session(
            True)

        return handler_input.response_builder.response


class OpcaoNoveIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name('OpcaoNoveIntent')(handler_input)

    
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dia = slots['Days'].value
        nome = slots['Cidade'].value
        day = []
        opc9 = []
        tempo = []
        lista = []
        opc99 = []
        data = []
        Ni = []
        alt = []
        altura = []

        filtro = airtable.search('Lugar', nome)

        for n, c in enumerate(filtro):
            lista.append(filtro[n]['fields'])


        for v, c in enumerate(lista):
            if lista[v]['Data'] == str(dia):
                opc9.append(lista[v]['Altura'])
                opc99.append(lista[v]['Hora'])


        for c in opc9:
            if float(c) < 1.0:
                altura.append('baixa')
            elif float(c) >= 1.0:
                altura.append('alta')

        
        data.append(dia[8])
        data.append(dia[9])
        values = ''.join(str(t) for t in data)

        RespostaFinal = f'Amanhã, Às {opc99[1]} a maré estará {altura[1]} com {opc9[1]}m de altura e às {opc99[2]} a maré estará {altura[2]} com {opc9[2]}m de altura.'

        handler_input.response_builder.speak(RespostaFinal).set_card(
            SimpleCard('Próximo dia', RespostaFinal)).set_should_end_session(
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
sb.add_request_handler(OpcaoUmIntentHandler())
sb.add_request_handler(OpcaoDoisIntentHandler())
sb.add_request_handler(OpcaoTresIntentHandler())
sb.add_request_handler(OpcaoQuatroIntentHandler())
sb.add_request_handler(OpcaoCincoIntentHandler())
sb.add_request_handler(OpcaoSeisIntentHandler())
sb.add_request_handler(OpcaoSeteIntentHandler())
sb.add_request_handler(OpcaoOitoIntentHandler())
sb.add_request_handler(OpcaoNoveIntentHandler())
sb.add_request_handler(NaoDesejaIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
