from sqlalchemy import Column, ForeignKey, BigInteger, SmallInteger, Float, String, DateTime, Date, Text, Boolean, \
    func, text, UUID, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine
import main.config as config


class Base(AsyncAttrs, DeclarativeBase):
    pass


# Таблица пользователей в которой состоят школьники и преподаватели
class Users(Base):
    __tablename__ = 'users'
    guid = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        server_default=text('uuid7()'),
        primary_key=True,
        autoincrement=False
    )
    login = Column(String(length=125), nullable=False)
    password = Column(String(length=125), nullable=False)
    hash_password = Column(String(length=255), nullable=False)
    phone_number = Column(BigInteger, nullable=False)
    fio = Column(String(length=255), nullable=False)
    birthday = Column(Date, nullable=False)
    gender = Column(String(length=20), nullable=False)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False,
        index=True
    )
    is_teacher = Column(Boolean, default=False, nullable=False, server_default=text('False'))


# Таблица вложений, где хранятся фотки, изображения достижений школьников
class Attachments(Base):
    __tablename__ = 'attachments'
    guid = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        server_default=text('uuid7()'),
        primary_key=True,
        autoincrement=False
    )
    type = Column(String(length=100), nullable=False)
    url = Column(String(length=255), nullable=False)
    path = Column(String(length=255), nullable=False)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False
    )
    is_deleted = Column(Boolean, default=False, nullable=False, server_default=text('False'))


# Таблица в которой хранятся наименования факторов и их весовые коэффициенты
class Factors(Base):
    __tablename__ = 'factors'
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(length=255), nullable=False)
    weight_factor = Column(Float, nullable=False)
    amount_of_points = Column(SmallInteger, default=1, nullable=False, server_default=text('1'))
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False
    )
    for_the_teacher = Column(Boolean, default=False, nullable=False, server_default=text('False'))


# Таблица достижений школьников
class Achievements(Base):
    __tablename__ = 'achievements'
    guid = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        server_default=text('uuid7()'),
        primary_key=True,
        autoincrement=False
    )
    user_guid = Column(UUID(as_uuid=False), ForeignKey(Users.guid), index=True, nullable=False)
    attachment_guid = Column(
        UUID(as_uuid=False),
        ForeignKey(Attachments.guid),
        nullable=False,
        server_default=text('uuid(\'00000000-0000-0000-0000-000000000000\')'),
        autoincrement=False,
        default='00000000-0000-0000-0000-000000000000'
    )
    description = Column(Text, nullable=False)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False,
        index=True
    )
    is_accepted = Column(Boolean, default=False, nullable=False, server_default=text('False'))
    is_deleted = Column(Boolean, default=False, nullable=False, server_default=text('False'))


# Таблица учебных классов
class Classes(Base):
    __tablename__ = 'classes'
    guid = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        server_default=text('uuid7()'),
        primary_key=True,
        autoincrement=False
    )
    name = Column(String(length=155), nullable=False)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False,
        index=True
    )
    is_deleted = Column(Boolean, default=False, nullable=False, server_default=text('False'))


# Таблица в которой хранится инфа об школьниках, которые состоят в определенном классе
class SchoolchildrenClasses(Base):
    __tablename__ = 'schoolchildren_classes'
    guid = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        server_default=text('uuid7()'),
        primary_key=True,
        autoincrement=False
    )
    class_guid = Column(UUID(as_uuid=False), ForeignKey(Classes.guid), index=True, nullable=False)
    user_guid = Column(UUID(as_uuid=False), ForeignKey(Users.guid), index=True, nullable=False)
    estimation = Column(Float, nullable=True)
    datetime_estimation_update = Column(DateTime, nullable=True)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False,
        index=True
    )
    is_deleted = Column(Boolean, default=False, nullable=False, server_default=text('False'))


# Таблица в которой хранится инфа об классах, в которых состоят преподаватели
class TeacherClasses(Base):
    __tablename__ = 'teacher_classes'
    __table_args__ = (PrimaryKeyConstraint('class_guid', 'user_guid'),)
    class_guid = Column(UUID(as_uuid=False), ForeignKey(Classes.guid), index=True, nullable=False)
    user_guid = Column(UUID(as_uuid=False), ForeignKey(Users.guid), index=True, nullable=False)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False
    )


# Таблица в которой хранятся вопросы для теста
class Questions(Base):
    __tablename__ = 'questions'
    id = Column(SmallInteger, primary_key=True)
    factor_id = Column(SmallInteger, ForeignKey(Factors.id), nullable=False)
    name = Column(String(length=255), nullable=False)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False
    )


# Таблица с пройденными тестами школьников
class Tests(Base):
    __tablename__ = 'tests'
    guid = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        server_default=text('uuid7()'),
        primary_key=True,
        autoincrement=False
    )
    user_guid = Column(UUID(as_uuid=False), ForeignKey(Users.guid), index=True, nullable=False)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False,
        index=True
    )
    is_accepted = Column(Boolean, default=False, nullable=False, server_default=text('False'))


class AnswersTests(Base):
    __tablename__ = 'answers_tests'
    guid = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        server_default=text('uuid7()'),
        primary_key=True,
        autoincrement=False
    )
    test_guid = Column(UUID(as_uuid=False), ForeignKey(Tests.guid), index=True, nullable=False)
    question_id = Column(SmallInteger, ForeignKey(Questions.id), nullable=False)
    score = Column(SmallInteger, default=1, nullable=False, server_default=text('1'))
    comment = Column(Text, nullable=True)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False
    )


# Таблица в которой хранятся сформированные рекомендации для школьников
class Recommendations(Base):
    __tablename__ = 'recommendations'
    guid = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        server_default=text('uuid7()'),
        primary_key=True,
        autoincrement=False
    )
    user_guid = Column(UUID(as_uuid=False), ForeignKey(Users.guid), index=True, nullable=False)
    description = Column(Text, nullable=False)
    datetime_create = Column(
        DateTime,
        default=func.now(),
        server_default=text('(now() AT TIME ZONE \'Asia/Novosibirsk\')'),
        nullable=False,
        index=True
    )
    is_neural = Column(Boolean, default=False, nullable=False, server_default=text('False'))
    is_accepted = Column(Boolean, default=False, nullable=False, server_default=text('False'))
    is_deleted = Column(Boolean, default=False, nullable=False, server_default=text('False'))


# alembic init -t async main/alembic
# alembic revision --autogenerate -m "init alembic"
# alembic upgrade head


engine = create_async_engine(
    f'postgresql+asyncpg://{config.DATABASE_USER}'
    f':{config.DATABASE_PASSWORD}'
    f'@{config.DATABASE_IP}:{config.DATABASE_PORT}'
    f'/{config.DATABASE_NAME}',
    echo=False,
    pool_recycle=300,
    query_cache_size=0,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=2,
    pool_use_lifo=True
)
