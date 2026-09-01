import pytest
from dashboard.queries import build_where_clause

def test_build_where_clause_empty():
    where_str, params = build_where_clause(state='ALL')
    assert where_str == ""
    assert params == {}

def test_build_where_clause_with_dates():
    where_str, params = build_where_clause(start_date='2020-01-01', end_date='2020-12-31', state='ALL')
    assert where_str == " AND o.order_purchase_timestamp >= %(start_date)s AND o.order_purchase_timestamp <= %(end_date)s"
    assert params == {'start_date': '2020-01-01', 'end_date': '2020-12-31'}

def test_build_where_clause_with_state():
    where_str, params = build_where_clause(state='SP')
    assert where_str == " AND c.customer_state = %(state)s"
    assert params == {'state': 'SP'}

def test_build_where_clause_all_params():
    where_str, params = build_where_clause(start_date='2021-01-01', end_date='2021-12-31', state='RJ')
    assert where_str == " AND o.order_purchase_timestamp >= %(start_date)s AND o.order_purchase_timestamp <= %(end_date)s AND c.customer_state = %(state)s"
    assert params == {'start_date': '2021-01-01', 'end_date': '2021-12-31', 'state': 'RJ'}
