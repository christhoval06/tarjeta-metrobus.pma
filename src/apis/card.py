from flask_restx import Namespace, Resource, fields

from src.tarjeta_metrobus import TarjetaMetrobusPanama
from src.tarjeta_metrobus.models import CardMovement

api = Namespace('card', description='Card related operations')

tmpma = TarjetaMetrobusPanama()

card_info_schema = api.model('CardInfo', {
    'noTarjeta': fields.String(description='The card number'),
    'estadoDeContrato': fields.String(description='The card status'),
    'saldoTarjeta': fields.String(description='The card balance'),
    'fechaSaldo': fields.String(description='The card last date'),
})

card_resume_schema = api.model('CardResume', {
    'noTarjeta': fields.String(description='The card number'),
    'estadoTarjeta': fields.String(description='The card status'),
    'tipoDeTarjeta': fields.String(description='The card type'),
    'saldoTarjeta': fields.String(description='The card balance')
})

card_movement_schema = api.model('CardMovement', {
    'noTransaccion': fields.String(description='The transaction number'),
    'movimiento': fields.String(description='The transaction type'),
    'fechaYHora': fields.String(description='The transaction datetime'),
    'lugar': fields.String(description='The transaction place'),
    'monto': fields.String(description='The transaction amount'),
    'saldoTarjeta': fields.String(description='The card balance after transaction')
})

card_stat_schema = api.model('CardStats', {
    'month': fields.String(),
    'amount': fields.String(),
    'count': fields.String()
})

card_stats_schema = api.model('CardStats', {
    'uses': fields.List(fields.Nested(card_stat_schema)),
    'charges': fields.List(fields.Nested(card_stat_schema)),
})


@api.route('/info/<int:number>', '/<int:number>/info')
@api.param('number', 'The card identifier')
@api.response(404, 'Card not found')
class CardInfo(Resource):
    '''Card information'''
    @api.doc('get_card_info')
    @api.marshal_with(card_info_schema)
    def get(self, number):
        '''Fetch a card given its identifier'''
        card_info = tmpma.get_card_info(number)
        if card_info is None:
            api.abort(404)

        return card_info.to_dict()


@api.route('/card_resume/<int:number>', '/<int:number>/resume')
@api.param('number', 'The card identifier')
@api.response(404, 'Card not found')
class CardResume(Resource):
    '''Card resume'''
    @api.doc('get_card_resume')
    @api.marshal_with(card_resume_schema)
    def get(self, number):
        '''Fetch a card resume given its identifier'''
        card_resume = tmpma.get_card_resume(number)
        if card_resume is None:
            api.abort(404)

        return card_resume.to_dict()


@api.route('/trx/<int:number>', '/<int:number>/trx', '/<int:number>/transactions')
class CardTransactions(Resource):
    '''Card transactions'''
    @api.doc('list_transactions')
    @api.marshal_list_with(card_movement_schema)
    def get(self, number):
        '''List all transactions'''
        transactions = tmpma.get_movements(number)
        if transactions is None:
            api.abort(404)

        return CardMovement.schema().dump(transactions, many=True)


@api.route('/resume/<int:number>', '/<int:number>/uses', '/<int:number>/stats', '/stats/<int:number>')
@api.param('number', 'The card identifier')
@api.response(404, 'Card not found')
class CardStats(Resource):
    '''Card stats'''
    @api.doc('get_card_stats')
    @api.marshal_with(card_stats_schema)
    def get(self, number):
        '''Fetch a card resume given its identifier'''
        card_resume = tmpma.get_card_resume_uses_charges(number)
        if card_resume is None:
            api.abort(404)

        return card_resume.to_dict()
