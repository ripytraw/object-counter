from typing import List, Optional

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from pymongo import MongoClient

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountInMemoryRepo(ObjectCountRepo):

    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):

    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)


class CountPostgresRepo(ObjectCountRepo):
    """
    PostgreSQL implementation of ObjectCountRepo.

    Maintains cumulative object counts per class.
    Uses atomic upsert to ensure concurrency-safe increments.
    """

    def __init__(self, db_url: str):
        self._engine: Engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            future=True,
        )

        self._metadata = MetaData()
        self._object_counts = Table(
            "object_counts",
            self._metadata,
            Column("object_class", String, primary_key=True),
            Column("count", Integer, nullable=False),
        )
        self._metadata.create_all(self._engine)

    def read_values(
        self,
        object_classes: Optional[List[str]] = None
    ) -> List[ObjectCount]:

        try:
            with self._engine.connect() as connection:
                stmt = select(self._object_counts)

                if object_classes:
                    stmt = stmt.where(
                        self._object_counts.c.object_class.in_(object_classes)
                    )

                result = connection.execute(stmt)

                return [
                    ObjectCount(
                        object_class=row.object_class,
                        count=row.count,
                    )
                    for row in result
                ]

        except SQLAlchemyError as exc:
            raise RuntimeError(
                "Failed to read object counts from Postgres"
            ) from exc

    def update_values(self, new_values: List[ObjectCount]) -> None:
        try:
            with self._engine.begin() as connection:
                for value in new_values:
                    stmt = insert(self._object_counts).values(
                        object_class=value.object_class,
                        count=value.count,
                    )

                    stmt = stmt.on_conflict_do_update(
                        index_elements=["object_class"],
                        set_={
                            "count": self._object_counts.c.count + value.count
                        },
                    )

                    connection.execute(stmt)

        except SQLAlchemyError as exc:
            raise RuntimeError(
                "Failed to update object counts in Postgres"
            ) from exc
    
    def close(self) -> None:
        """Dispose underlying connection pool."""
        self._engine.dispose()
