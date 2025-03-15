from sqlalchemy import select, update, insert, delete


class CRUD:
    session = None
    model = None

    def __init__(self, session, model):
        self.session = session
        self.model = model

    async def get(self, query, _all, extended_query: bool = False):
        async with self.session() as session:
            result = await session.execute(query)
            result = result.all() if _all else result.first()
            if result is None or result == list():
                return None
            if _all:
                return tuple(x[0] for x in result) if not extended_query else result
            return result[0] if not extended_query else result

    async def read(
            self,
            _where: list = list(),
            _all: bool = False
    ) -> None | object | tuple[object]:
        query = select(self.model).where(*_where)
        return await self.get(query=query, _all=_all)

    async def extended_query(
            self,
            _select: list | None = None,
            _join: list | None = None,
            _where: list = list(),
            _all: bool = False,
            _order_by: list | None = None,
            _group_by: list | None = None
    ) -> object:
        if _select is None or _select == []:
            raise Exception("_select is None or don't have values")
        query = select(*_select)

        if _join is not None or _join != []:
            for i in _join:
                query = query.join(*i, isouter=True)

        if _group_by:
            query = query.group_by(*_group_by)

        if _order_by:
            query = query.order_by(*_order_by)

        query = query.where(*_where)
        return await self.get(query=query, _all=_all, extended_query=True)

    async def create(self, _values: dict) -> object:
        if _values is None or _values == {}:
            raise Exception("_value is None or don't have values")
        async with self.session() as session:
            r = await session.execute(insert(self.model).values(**_values).returning(self.model))
            return r.first()[0]

    async def update(self, _where: list, _values: dict) -> list[object]:
        if _values is None or _values == {}:
            raise Exception("_value is None or don't have values")
        if _where is None or _where == []:
            raise Exception("_where is None or don't have values")
        async with self.session() as session:
            result = await session.execute(update(self.model).where(*_where).values(**_values).returning(self.model))
            return tuple(x[0] for x in result.all())

    async def delete(self, _where: list) -> None:
        if _where is None or _where == []:
            print('Упс... Удалились все данные в таблице')
        async with self.session() as session:
            await session.execute(delete(self.model).where(*_where))

