# -*- coding: utf-8 -*-
'''
 Models for Tarjeta Metrobus Panama
'''
from enum import Enum
from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, DataClassJsonMixin



class Services(Enum):
    '''
    Metrobus services
    '''
    SESSION = 'SesionPortalServlet'
    COMMERCE = 'ComercialesPortalServlet'


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
