import model
from datetime import date


def test_order_line_mapper_can_load_lines(session):
    session.execute(
        "INSERT INTO order_lines (order_id, sku, qty) VALUES "
        '("order1", "RED-CHAIR", 12),'
        '("order1", "RED-TABLE", 13),'
        '("order2", "BLUE-LIPSTICK", 14)'
    )

    expected = [
        model.OrderLine("order1", "RED-CHAIR", 12),
        model.OrderLine("order1", "RED-TABLE", 13),
        model.OrderLine("order2", "BLUE-LIPSTICK", 14)
    ]
    assert session.query(model.OrderLine).all() == expected


def test_order_line_mapper_can_lines(session):
    new_line = model.OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute("SELECT order_id, sku, qty FROM order_lines;"))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]


def test_retrieving_batches(session):
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        " VALUES ('batch1', 'sku1', 100, null)"
    )

    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        " VALUES ('batch2', 'sku2', 200, '2011-04-11')"
    )

    expected = [
        model.Batch("batch1", "sku1", 100, eta=None),
        model.Batch("batch2", "slu2", 200, eta=date(2011, 4, 11))
    ]

    assert session.query(model.Batch).all() == expected


def test_saving_batches(session):
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    session.add(batch)
    session.commit()

    rows = session.execute(
        "SELECT reference, sku, _purchased_quantity, eta FROM batches"
    )
    assert list(rows) == [("batch1", "sku1", 100, None)]


def test_saving_allocations(session):
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    line = model.OrderLine("order1", "sku1", 10)
    batch.allocate(line)
    session.add(batch)
    session.commit()
    rows = list(session.execute(
        "SELECT order_line_id, batch_id FROM allocations"
    ))
    assert rows == [(line.id, batch.id)]


def test_retrieving_allocations(session):
    session.execute(
        "INSERT INTO order_lines (order_id, sku, qty) VALUES "
        "('order1', 'sku1', 12)"
    )

    [[ol_id]] = session.execute(
        "SELECT id FROM order_lines WHERE order_id = :order_id AND sku = :sku",
        dict(order_id="order1", sku="sku1")
    )

    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES "
        "('batch1', 'sku1', 100, null)"
    )

    [[b_id]] = session.execute(
        "SELECT id FROM batches WHERE reference = :reference and sku = :sku",
        dict(reference="batch1", sku="sku1")
    )

    session.execute(
        "INSERT INTO allocations (order_line_id, batch_id) VALUES "
        "(:ol_id, :b_id)",
        dict(ol_id=ol_id, b_id=b_id)
    )

    batch = session.query(model.Batch).one()
    assert batch._allocations == {model.OrderLine("order1", "sku1", 12)}
