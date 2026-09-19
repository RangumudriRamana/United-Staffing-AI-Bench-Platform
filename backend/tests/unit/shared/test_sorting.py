from sqlalchemy import column, select

from app.shared.sorting import apply_sorting_to_query


class ModelWithId:
    id = column("id")
    name = column("name")


class ModelWithoutId:
    name = column("name")


def test_apply_sorting_without_sort_by_uses_id_desc():
    query = select(ModelWithId.name)

    result = apply_sorting_to_query(
        query=query,
        model=ModelWithId,
        sort_by=None,
        sort_order="asc",
    )

    sql = str(result)

    assert "ORDER BY id DESC" in sql


def test_apply_sorting_invalid_column_uses_id_desc():
    query = select(ModelWithId.name)

    result = apply_sorting_to_query(
        query=query,
        model=ModelWithId,
        sort_by="does_not_exist",
        sort_order="asc",
    )

    sql = str(result)

    assert "ORDER BY id DESC" in sql


def test_apply_sorting_valid_column_ascending():
    query = select(ModelWithId.name)

    result = apply_sorting_to_query(
        query=query,
        model=ModelWithId,
        sort_by="name",
        sort_order="asc",
    )

    sql = str(result)

    assert "ORDER BY name ASC" in sql


def test_apply_sorting_valid_column_descending():
    query = select(ModelWithId.name)

    result = apply_sorting_to_query(
        query=query,
        model=ModelWithId,
        sort_by="name",
        sort_order="desc",
    )

    sql = str(result)

    assert "ORDER BY name DESC" in sql


def test_apply_sorting_invalid_column_without_id_returns_original_query():
    query = select(ModelWithoutId.name)

    result = apply_sorting_to_query(
        query=query,
        model=ModelWithoutId,
        sort_by="does_not_exist",
        sort_order="desc",
    )

    assert result is query