# -*- coding: utf-8 -*-
'''
Web scraping API for Tarjeta Metrobus Panama
'''
# from __future__ import annotations
import datetime
from enum import Enum
from typing import List, Union
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, DataClassJsonMixin

import pandas as pd
import requests

from bs4 import BeautifulSoup, Tag
from pytz import timezone
from slugify import slugify

__author__ = "Christhoval Barba"
__copyright__ = "Copyright 2024, GND labs"
__credits__ = ["Christhoval Barba"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christhoval Barba"
__email__ = "me@christhoval.dev"

URL = "http://200.46.245.230:8080/PortalCAE-WAR-MODULE"
DEFAULT_HEADERS = {
    "Content-Type":
    "application/x-www-form-urlencoded",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36",
}


class Services(Enum):
    '''
    Metrobus services
    '''
    SESSION = 'SesionPortalServlet'
    COMMERCE = 'ComercialesPortalServlet'


def get_session() -> requests.Session:
    '''
    Get a session to the portal

    Returns:
        requests.Session
    '''
    _session = requests.Session()
    _session.headers.update(DEFAULT_HEADERS)
    _session.request("GET", URL, timeout=15)

    return _session


session = get_session()

# https://github.com/andrew962/metrobus-api/blob/master/init.py

# https://json2pyi.pages.dev/#Dataclass

# https://github.com/qzxtu/Metro-Consulta/blob/main/js/main.js


@dataclass
class ComercialesParams(DataClassJsonMixin):
    '''
    Data class for comerciales parameters
    '''
    KSI: str
    accion: int
    itemms: int
    item: int
    DiasMov: int
    fechalogeo: str
    FechaInicioMovimientos: str


def get_comerciales_params(card_number: str, itemms: str, item: str, accion: str) -> Union[ComercialesParams, None]:
    '''
    Get comerciales parameters

    Args:
        card_number (str): Card number
        itemms (str): itemms
        item (str): item
        accion (str): accion
    Returns:
        Union[ComercialesParams, None]: ComercialesParams
    '''

    card_info = get_card_info(card_number, only_ksi=True)

    if card_info is None:
        return None

    now = datetime.datetime.now(tz=timezone('America/Panama'))
    now_formated = now.strftime('%Y%m%d%H%M%S')

    return ComercialesParams.from_dict({
        'KSI': card_info.ksi,
        'accion': accion,
        'itemms': itemms,
        'item': item,
        'DiasMov': 45,
        'fechalogeo': now_formated,
        'FechaInicioMovimientos': '',
    })


@dataclass_json
@dataclass
class KSI:
    '''
    Dataclass to store session id
    '''
    ksi: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CardInfo(DataClassJsonMixin):
    '''
    Dataclass to store card information
    '''
    no_tarjeta: str
    estado_de_contrato: str
    saldo_tarjeta: str
    fecha_saldo: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CardInfoResume(DataClassJsonMixin):
    '''
    Dataclass to store card resume information
    '''
    no_tarjeta: str
    estado_tarjeta: str
    tipo_de_tarjeta: str
    saldo_tarjeta: str


def bs_table_to_dict(table: Tag):
    '''
    Convert a bs4 table to a dict

    Args:
        table (Tag): bs4 table
    Returns:
        dict
    '''

    data = {}
    table_data = [[cell.text for cell in row("td")] for row in table.find_all("tr")]

    table_data = [*table_data[0], *table_data[1]]

    for i in range(0, len(table_data), 2):
        data[slugify(table_data[i], separator='_')] = (table_data[i + 1]).strip()

    return data


def get_card_resume(card_number: str) -> Union[CardInfoResume, None]:
    '''
    Get card info from resume
    Args:
    card_number (str): Card number

    Returns:
        Union[KeySesionId, CardInfo]: Card info
    '''
    params = get_comerciales_params(card_number, 2000, 1, 6)

    if params is None:
        return None

    url = f'{URL}/{Services.COMMERCE.value}'
    res = session.request("GET", url, params=params.to_dict(), timeout=15)

    soup = BeautifulSoup(res.text, "html.parser")

    card_info = {}

    card_balance = soup.find(string='Saldo tarjeta:')

    card_info_table = None
    if card_balance is None:
        return None

    card_info_table = card_balance.parent.parent.parent

    if card_info_table is None:
        return None

    card_info = bs_table_to_dict(card_info_table)
    return CardInfoResume.from_dict(card_info)


def get_card_info(card_number: str, only_ksi: bool = False) -> Union[KSI, CardInfo, None]:
    '''
    Get card info
    Args:
    card_number (str): Card number
    only_ksi (bool, optional): Only return KSI. Defaults to False.

    Returns:
        Union[KeySesionId, CardInfo]: Card info
    '''
    params = {
        'accion': 6,
        'NumDistribuidor': 99,
        'NomUsuario': 'usuInternet',
        'NomHost': 'AFT',
        'NonDominio': 'aft.cl',
        'RutUsuario': '0',
        'NumTarjeta': card_number,
        'bloqueable': ''
    }

    url = f'{URL}/{Services.SESSION.value}'
    
    res = session.request("GET", url, params=params, timeout=15)

    soup = BeautifulSoup(res.text, "html.parser")

    card_info = {}

    ksi_input = soup.find(attrs={'name': 'KSI'})
    ksi_value = ksi_input['value']

    if ksi_input is None:
        return None

    card_info['ksi'] = ksi_value

    if only_ksi:
        return KSI(ksi=ksi_value)

    card_balance = soup.find(string='Saldo  tarjeta:')

    card_info_table = None
    if card_balance is None:
        return None

    card_info_table = card_balance.parent.parent.parent

    if card_info_table is None:
        return None

    card_info = bs_table_to_dict(card_info_table)
    return CardInfo.from_dict(card_info)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CardMovement(DataClassJsonMixin):
    '''
    Dataclass to store card movements
    '''
    no_transaccion: str
    movimiento: str
    fecha_y_hora: str
    lugar: str
    monto: str
    saldo_tarjeta: str


def get_movements(card_number) -> Union[List[CardMovement], None]:
    '''
    Get movements for a card number

    Args:
        card_number (str): Card number to get movements for

    Returns:
        Union[List[CardMovement], None]: Movements
    '''
    params = get_comerciales_params(card_number, 3000, 2, 1)

    if params is None:
        return None

    url = f'{URL}/{Services.COMMERCE.value}'
    res = session.request("GET", url, params=params.to_dict(), timeout=15)

    soup = BeautifulSoup(res.text, "html.parser")

    table_title = soup.find(string='Saldos y movimientos')
    if table_title is None:
        return None

    table = table_title.parent.parent.parent.parent
    table_data = [[cell.text.strip() for cell in row("td")] for row in table.find_all("tr")]

    header_name = ['to_drop', *[slugify(x, separator='_') for x in table_data[1][1:]]]

    table_data = table_data[2::]
    df = pd.DataFrame(table_data)
    df.columns = header_name
    df = df.drop('to_drop', axis=1)
    # df['fecha_y_hora'] = pd.to_datetime(df['fecha_y_hora'], format='%d/%m/%Y %H:%M')
    # df.to_json(orient='records')
    # data = CardMovement.schema().load(df.to_json(orient='records'), many=True)
    # CardMovement.schema().dump(data, many=True)

    return df.apply(lambda row: CardMovement(**row), axis=1).tolist()


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CardStat(DataClassJsonMixin):
    '''
    Dataclass to store card statistics
    '''
    month: str
    amount: str
    count: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CardStats(DataClassJsonMixin):
    '''
    Dataclass to store card statistics
    '''
    uses: List[CardStat]
    charges: List[CardStat]


def get_card_resume_uses_charges(card_number: str) -> Union[CardInfoResume, None]:
    '''
    Get card uses and charges resume in last 3 months
    Args:
    card_number (str): Card number

    Returns:
        Union[KeySesionId, CardInfo]: Card info
    '''
    params = get_comerciales_params(card_number, 2000, 1, 6)

    if params is None:
        return None

    url = f'{URL}/{Services.COMMERCE.value}'
    res = session.request("GET", url, params=params.to_dict(), timeout=15)

    soup = BeautifulSoup(res.text, "html.parser")

    def table_to_data(text_in_table):
        table_tile = soup.find(string=text_in_table)
        if table_tile is None:
            return None

        table = table_tile.parent.parent.parent.parent
        table_data = [[cell.text.strip() for cell in row("td")] for row in table.find_all("tr")]

        table_data = table_data[1::]
        keys = ['month', 'amount', 'count']
        merged_columns = zip(table_data[0][1:], table_data[1][1:],  table_data[2][1:])

        return [dict(zip(keys, values)) for values in merged_columns]

    data = CardStats(
        uses=CardStat.schema().load(table_to_data('Monto utilizado'), many=True),
        charges=CardStat.schema().load(table_to_data('Monto cargado'), many=True))

    return data


if __name__ == '__main__':
    print(get_card_info('33070524'))
    print(get_card_resume('33070524'))
    # print(get_movements('33070524'))
    print(get_card_resume_uses_charges('33070524'))
