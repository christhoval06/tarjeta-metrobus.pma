# -*- coding: utf-8 -*-
'''
Web scrapper for Tarjeta Metrobus Panama
'''
# from __future__ import annotations
import datetime
from typing import List, Union

import pandas as pd
import requests

from bs4 import BeautifulSoup, Tag
from pytz import timezone
from slugify import slugify

from src.core.singleton import SingletonMeta

from .models import (KSI,
                     CardStat,
                     CardStats,
                     Services,
                     CardInfo,
                     CardInfoResume,
                     CardMovement,
                     ComercialesParams)
from .utils import bs_table_to_dict, table_to_data

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

class TarjetaMetrobusPanama(metaclass=SingletonMeta):
    '''
    Tarjeta Metrobus Panama
    '''
    
    session: requests.Session = None

    def __init__(self) -> None:
        self.session = self.get_session()
        
        
    def get_session(self, ) -> requests.Session:
        '''
        Get a session to the portal

        Returns:
            requests.Session
        '''
        _session = requests.Session()
        _session.headers.update(DEFAULT_HEADERS)
        _session.request("GET", URL, timeout=15)

        return _session


    def get_comerciales_params(self, card_number: str, itemms: str, item: str, accion: str) -> Union[ComercialesParams, None]:
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

        card_info = self.get_card_info(card_number, only_ksi=True)

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


    def get_card_resume(self, card_number: str) -> Union[CardInfoResume, None]:
        '''
        Get card info from resume
        Args:
        card_number (str): Card number

        Returns:
            Union[KeySesionId, CardInfo]: Card info
        '''
        params = self.get_comerciales_params(card_number, 2000, 1, 6)

        if params is None:
            return None
        
        self.session = self.get_session()

        url = f'{URL}/{Services.COMMERCE.value}'
        res = self.session.request("GET", url, params=params.to_dict(), timeout=15)

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


    def get_card_info(self, card_number: str, only_ksi: bool = False) -> Union[KSI, CardInfo, None]:
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
        
        self.session = self.get_session()

        url = f'{URL}/{Services.SESSION.value}'
        res = self.session.request("GET", url, params=params, timeout=15)

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


    def get_movements(self, card_number) -> Union[List[CardMovement], None]:
        '''
        Get movements for a card number

        Args:
            card_number (str): Card number to get movements for

        Returns:
            Union[List[CardMovement], None]: Movements
        '''
        params = self.get_comerciales_params(card_number, 3000, 2, 1)

        if params is None:
            return None
        
        self.session = self.get_session()

        url = f'{URL}/{Services.COMMERCE.value}'
        res = self.session.request("GET", url, params=params.to_dict(), timeout=15)

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


    def get_card_resume_uses_charges(self, card_number: str) -> Union[CardInfoResume, None]:
        '''
        Get card uses and charges resume in last 3 months
        Args:
        card_number (str): Card number

        Returns:
            Union[KeySesionId, CardInfo]: Card info
        '''
        params = self.get_comerciales_params(card_number, 2000, 1, 6)

        if params is None:
            return None
        
        self.session = self.get_session()

        url = f'{URL}/{Services.COMMERCE.value}'
        res = self.session.request("GET", url, params=params.to_dict(), timeout=15)

        soup = BeautifulSoup(res.text, "html.parser")

        data = CardStats(
            uses=CardStat.schema().load(table_to_data(soup, 'Monto utilizado'), many=True),
            charges=CardStat.schema().load(table_to_data(soup, 'Monto cargado'), many=True))

        return data
