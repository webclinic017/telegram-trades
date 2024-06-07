from typing import List, Dict
from constants import FUTL, UTIL, logging

SLP = 1

trade_keys = [
    "order_id",
    "exchange",
    "filled_timestamp",
    "filled_quantity",
    "exchange_order_id",
    "price",
    "side",
]
position_keys = [
    "symbol",
    "quantity",
    "product",
    "last_price",
    "exchange",
    "day_buy_value",
    "day_sell_value",
    "MtoM",
]
order_keys = [
    "symbol",
    "quantity",
    "side",
    "price",
    "trigger_price",
    "average_price",
    "filled_quantity",
    "exchange",
    "order_id",
    "broker_timestamp",
    "product",
    "remarks",
    "order_type",
    "Status",
]


def update_lst_of_dct_with_vals(lst_of_dct, key, **kwargs):
    updated = False
    for dct in lst_of_dct:
        if dct.get(key, None) == kwargs[key]:
            dct.update(**kwargs)
            updated = True
            break
    if not updated:
        lst_of_dct.append(kwargs)
    return lst_of_dct


def filter_by_keys(keys: List, lst: List[Dict]) -> List[Dict]:
    new_lst = []
    if lst and isinstance(lst, list) and any(lst):
        for dct in lst:
            new_dct = {}
            for key in keys:
                if dct.get(key, None):
                    new_dct[key] = dct[key]
            new_lst.append(new_dct)
    return new_lst


def filtered_positions(api):
    UTIL.slp_for(SLP)
    lst = filter_by_keys(position_keys, api.positions)
    return lst


def filtered_orders(api, order_id):
    UTIL.slp_for(SLP)
    lst = api.orders
    # print(lst[0].keys())

    lst = filter_by_keys(order_keys, api.orders)
    if order_id:
        lst_order = [order for order in lst if order["order_id"] == order_id]
        logging.debug(lst_order)
        if any(lst_order):
            return lst_order[0]
    return [order for order in lst]


def get_order_from_book(api, resp):
    dct_order = {"Status": "E-ORDERBOOK"}
    order_1 = resp.get("NOrdNo", None)
    order_2 = resp.get("nestOrderNumber", None)
    order_id = order_1 if order_1 else order_2
    if order_id:
        UTIL.slp_for(1)
        dct_order = filtered_orders(api, order_id)
    return dct_order


def square_off(api, order_id, symbol, quantity):
    args = dict(
        order_id=order_id,
        symbol=symbol,
        side="S",
        quantity=quantity,
        price=0.0,
        order_type="MKT",
        product="N",
    )
    resp = api.order_modify(**args)
    logging.info(f"modify SL {args} to tgt got {resp}")


def modify_order(api, order: Dict) -> Dict:
    args = dict(
        order_id=order["order_id"],
        symbol=order["symbol"],
        side=order["side"],
        quantity=order["quantity"],
        price=order["price"],
        trigger_price=order["trigger_price"],
        order_type=order["order_type"],
        product=order["product"],
    )
    resp = api.order_modify(**args)
    return resp


def market_order(api, order, action: str):
    """
    input:
        api: broker object
        order: order details
        action: condition for param switch
    output:
        resp
    """
    if action == "opposite":
        side = "S"
        price = 0.0
        trigger_price = 0.0
        order_type = "MKT"

    args = dict(
        side=side,
        price=price,
        trigger_price=trigger_price,
        order_type=order_type,
        symbol=order["exchange"] + ":" + order["symbol"],
        quantity=order["quantity"],
        product="N",
        remarks=order["remarks"],
    )
    resp = api.order_place(**args)
    logging.info(f"order {action} {args} got {resp}")
    return resp


def download_masters(broker):
    exchanges = ["NFO", "BFO"]
    for exchange in exchanges:
        if FUTL.is_file_not_2day(f"./{exchange}.csv"):
            broker.get_contract_master(exchange)
            UTIL.slp_for(SLP)


def get_ltp(broker, exchange, symbol):
    UTIL.slp_for(SLP)
    obj_inst = broker.get_instrument_by_symbol(exchange, symbol)
    UTIL.slp_for(SLP)
    return float(broker.get_scrip_info(obj_inst)["Ltp"])


if __name__ == "__main__":
    from constants import BRKR, DATA
    from login import get_broker
    import pandas as pd
    from rich import print

    api = get_broker(BRKR)

    lst = filtered_positions(api)
    if any(lst):
        pos = pd.DataFrame(lst).set_index("symbol")
        print(pos)
        pos.to_csv(DATA + "pos.csv")

    lst = filtered_orders(api, None)
    if any(lst):
        ord = pd.DataFrame(lst).set_index("order_id")
        print(ord)
        ord.to_csv(DATA + "ord.csv")

    """

    updates = {
        "order_type": "MKT",
    }

    print(lst)
    for order in lst:
        UTIL.slp_til_nxt_sec()
        if any(order):
            resp = api.order_modify(**order)
            if not isinstance(resp, dict):
                print("something is wrong")
            elif isinstance(resp, dict) and resp.get("status", "Not_Ok") == "Not_Ok":
                print(resp)
    args = dict(
        symbol="NSE:TRIDENT",
        side="Sell",
        quantity=1,
        price=40.00,
        trigger_price=40.05,
        order_type="SL",
        product="MIS"
    )
    resp = api.order_place(**args)
    if resp and resp.get("NOrdNo", None):
        print(f"{resp['NOrdNo']} successfully placed")
    else:
        print(f"{resp=}")

    order_cancelled = api.order_cancel("24012400365338")
    print(f"{order_cancelled=}")

    order_id = "24012400368866"
    norder = order_modify(lst, order_id)
    if norder and any(norder):
        print(norder)
        norder["symbol"] = norder["exchange"] + ":" + norder["symbol"]
        norder["quantity"] = 2
        norder["order_type"] = "MKT"
        norder.pop("price", None)
        norder.pop("trigger_price", None)
        modified_order = api.order_modify(**norder)
        print(f"{modified_order=}")
    """
