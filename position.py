import json
from binance.enums import *
from decimal import Decimal


class Position:
    """單一種貨幣的倉位"""

    def __init__(self, asset_symbol, on_update, dict):
        """
        asset_symbol: 貨幣代號
        transaction: 交易紀錄
        """
        self.asset_symbol = asset_symbol
        self.__on_update_transaction = on_update
        self.transactions = list()

        if dict is None:
            self.open_quantity = Decimal(0.0)
            self.open_cost = Decimal(0.0)
            self.realized_gain = Decimal(0.0)
            self.total_commission_as_usdt = Decimal(0.0)
            return

        # print(dict)
        self.open_quantity = Decimal(dict['open_quantity'])
        self.open_cost = Decimal(dict['open_cost'])
        self.realized_gain = Decimal(dict['realized_gain'])
        self.total_commission_as_usdt = Decimal(dict['total_commission_as_usdt'])

        for transact in dict['transactions']:
            # print(transact)
            self.transactions.append(Transaction(
                int(transact['time']),
                transact['activity'],
                transact['symbol'],
                transact['trade_symbol'],
                Decimal(transact['quantity']),
                Decimal(transact['price']),
                Decimal(transact['commission']),
                transact['commission_asset']),
                Decimal(transact['commission_as_usdt']),
                transact['trade_id'],
                transact['closed_trade_ids'])

    def to_dict(self):
        return {
            'open_quantity': str(self.open_quantity),
            'open_cost': str(self.open_cost),
            'realized_gain': str(self.realized_gain),
            'total_commission_as_usdt': str(self.total_commission_as_usdt),
            'transactions': [t.to_dict() for t in self.transactions],
        }

    def add_transaction(self, transaction):
        if transaction.activity == SIDE_BUY:
            self.open_quantity += transaction.quantity
            self.open_cost += transaction.quantity * transaction.price
        elif transaction.activity == SIDE_SELL:
            current_avg_price = self.open_cost / self.open_quantity
            purchase_cost = transaction.quantity * current_avg_price
            realized_gain = (transaction.price -
                             current_avg_price) * transaction.quantity

            # print(f"current_avg_price = {current_avg_price}")
            # print(f"purchase_cost = {purchase_cost}")
            # print(f"realized_gain = {realized_gain}")

            self.open_quantity -= transaction.quantity
            self.open_cost -= purchase_cost
            self.realized_gain += realized_gain
        else:
            raise Exception("Unknown transaction activity")

        self.total_commission_as_usdt += transaction.commission_as_usdt
        self.transactions.append(transaction)
        self.__on_update_transaction(self.asset_symbol)

    def get_transactions_count(self):
        """取得交易完成總數"""
        return len(self.transactions)

    def __str__(self):
        if self.open_quantity > 0:
            return f"{str(self.asset_symbol)}: {str(self.open_quantity)} @{str(self.open_cost)}"
            f", realized = {str(self.realized_gain)}"

        return f"{str(self.asset_symbol)}: no position, realized = {str(self.realized_gain)}"


class Transaction:
    def __init__(self, time, activity, symbol, trade_symbol, quantity, price, commission, commission_asset, commission_as_usdt, trade_id, closed_trade_ids):
        self.time = time
        self.activity = activity
        self.symbol = symbol
        self.trade_symbol = trade_symbol
        self.quantity = quantity
        self.price = price
        self.commission = commission
        self.commission_asset = commission_asset
        self.commission_as_usdt = commission_as_usdt
        self.trade_id = trade_id

        if activity == SIDE_SELL and (closed_trade_ids is None or len(closed_trade_ids) < 1):
            print("Warning: closed_trade_ids not specified for a SELL transaction")

        if closed_trade_ids is None:
            self.closed_trade_ids = []
        else:
            self.closed_trade_ids = closed_trade_ids

    def to_dict(self):
        return {
            'time': str(self.time),
            'activity': str(self.activity),
            'symbol': str(self.symbol),
            'trade_symbol': str(self.trade_symbol),
            'quantity': str(self.quantity),
            'price': str(self.price),
            'commission': str(self.commission),
            'commission_asset': str(self.commission_asset),
            'commission_as_usdt': str(self.commission_as_usdt),
            'trade_id': str(self.trade_id),
            'closed_trade_ids': self.closed_trade_ids
        }
