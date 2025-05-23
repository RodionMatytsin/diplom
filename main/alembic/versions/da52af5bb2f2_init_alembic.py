"""init alembic

Revision ID: da52af5bb2f2
Revises: 
Create Date: 2025-05-23 23:51:56.476532

"""
from typing import Sequence, Union
import main.config as config
from alembic import op
import sqlalchemy as sa


revision: str = 'da52af5bb2f2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute('create EXTENSION if not exists "uuid-ossp"')

    op.execute(
        'create or replace function uuid7() returns uuid as $$ declare '
        'v_time numeric := null; '
        'v_unix_t numeric := null; '
        'v_rand_a numeric := null; '
        'v_rand_b numeric := null; '
        'v_unix_t_hex varchar := null; '
        'v_rand_a_hex varchar := null; '
        'v_rand_b_hex varchar := null; '
        'v_output_bytes bytea := null; '
        'c_milli_factor numeric := 10^3::numeric; '
        'c_micro_factor numeric := 10^6::numeric; '
        'c_scale_factor numeric := 4.096::numeric; '
        'c_version bit(64) := x\'0000000000007000\'; '
        'c_variant bit(64) := x\'8000000000000000\'; '
        'begin '
        'v_time := extract(epoch from clock_timestamp()); '
        'v_unix_t := trunc(v_time * c_milli_factor); '
        'v_rand_a := ((v_time * c_micro_factor) - (v_unix_t * c_milli_factor)) * c_scale_factor; '
        'v_rand_b := random()::numeric * 2^62::numeric; '
        'v_unix_t_hex := lpad(to_hex(v_unix_t::bigint), 12, \'0\'); '
        'v_rand_a_hex := lpad(to_hex((v_rand_a::bigint::bit(64) | c_version)::bigint), 4, \'0\'); '
        'v_rand_b_hex := lpad(to_hex((v_rand_b::bigint::bit(64) | c_variant)::bigint), 16, \'0\'); '
        'return (v_unix_t_hex || v_rand_a_hex || v_rand_b_hex)::uuid; '
        'end $$ language plpgsql; '
    )

    op.create_table(
        'attachments',
        sa.Column(
            'guid',
            sa.UUID(as_uuid=False),
            server_default=sa.text('uuid7()'),
            autoincrement=False,
            nullable=False
        ),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.PrimaryKeyConstraint('guid')
    )
    op.create_index(op.f('ix_attachments_guid'), 'attachments', ['guid'], unique=True)

    op.execute(
        f'insert into attachments (guid, type, url, path) '
        f'values ('
        f'\'00000000-0000-0000-0000-000000000000\', '
        f'\'image/jpeg\', '
        f'\'{config.API_MEDIA}00000000-0000-0000-0000-000000000000\', '
        f'\'{config.MEDIA_FOLDER}/default.png\''
        f')'
    )

    op.create_table(
        'classes',
        sa.Column(
            'guid',
            sa.UUID(as_uuid=False),
            server_default=sa.text('uuid7()'),
            autoincrement=False,
            nullable=False
        ),
        sa.Column('name', sa.String(length=155), nullable=False),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.PrimaryKeyConstraint('guid')
    )
    op.create_index(op.f('ix_classes_datetime_create'), 'classes', ['datetime_create'], unique=False)
    op.create_index(op.f('ix_classes_guid'), 'classes', ['guid'], unique=True)

    op.create_table(
        'questions',
        sa.Column('id', sa.SmallInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('amount_of_points', sa.SmallInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.execute(
        'insert into questions (name, amount_of_points) values (\'Какой предмет или область знаний вам наиболее интересна? '
        'Оцените свой интерес по шкале от 1 до 10, где 1 — неинтересно, а 10 — очень интересно.\', 10)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Насколько вы мотивированы учиться и достигать своих целей? '
        'Оцените свою внутреннюю мотивацию по шкале от 1 до 10.\', 10)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Насколько вы уверены в своих учебных целях и планах на будущее? '
        'Оцените свою определенность по шкале от 1 до 10.\', 10)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете условия, в которых учитесь? Оцените качество '
        'комфорта в учебной среде по шкале от 1 до 5.\', 5)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете свои финансовые возможности для дополнительных '
        'занятий и кружков? Оцените по шкале от 1 до 5, где 1 — очень ограниченные возможности.\', 5)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете свои отношения с преподавателями и одноклассниками? '
        'Оцените по шкале от 1 до 5, где 1 — плохие отношения.\', 5)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете качество преподавания в вашей школе? Оцените по шкале '
        'от 1 до 10, где 1 — очень плохо, 10 — отлично.\', 10)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете качество учебных материалов и методик, используемых '
        'в школе? Оцените по шкале от 1 до 10.\', 10)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете наличие необходимого оборудования и материалов для '
        'обучения? Оцените по шкале от 1 до 5.\', 5)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете престиж вашей школы или учебной программы? '
        'Оцените по шкале от 1 до 5, где 1 — низкий престиж.\', 5)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете свои возможности участия в дополнительных занятиях '
        'или кружках? Оцените по шкале от 1 до 10.\', 10)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете свои личные таланты и способности? '
        'Оцените по шкале от 1 до 10, где 1 — низкие способности.\', 10)')
    op.execute(
        'insert into questions (name, amount_of_points) values (\'Как вы оцениваете свои цели и планы на будущее? Оцените по шкале '
        'от 1 до 5, где 1 — нет четких целей.\', 5)')

    op.create_table(
        'users',
        sa.Column(
            'guid',
            sa.UUID(as_uuid=False),
            server_default=sa.text('uuid7()'),
            autoincrement=False,
            nullable=False
        ),
        sa.Column('login', sa.String(length=125), nullable=False),
        sa.Column('password', sa.String(length=125), nullable=False),
        sa.Column('hash_password', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.BigInteger(), nullable=False),
        sa.Column('fio', sa.String(length=255), nullable=False),
        sa.Column('birthday', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=False),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.Column('is_teacher', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.PrimaryKeyConstraint('guid')
    )
    op.create_index(op.f('ix_users_datetime_create'), 'users', ['datetime_create'], unique=False)
    op.create_index(op.f('ix_users_guid'), 'users', ['guid'], unique=True)

    op.create_table(
        'achievements',
        sa.Column(
            'guid',
            sa.UUID(as_uuid=False),
            server_default=sa.text('uuid7()'),
            autoincrement=False,
            nullable=False
        ),
        sa.Column('user_guid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column(
            'attachment_guid',
            sa.UUID(as_uuid=False),
            server_default=sa.text("uuid('00000000-0000-0000-0000-000000000000')"),
            autoincrement=False,
            nullable=True
        ),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.Column('is_accepted', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.ForeignKeyConstraint(['user_guid'], ['users.guid'], ),
        sa.PrimaryKeyConstraint('guid')
    )
    op.create_index(op.f('ix_achievements_datetime_create'), 'achievements', ['datetime_create'], unique=False)
    op.create_index(op.f('ix_achievements_guid'), 'achievements', ['guid'], unique=True)
    op.create_index(op.f('ix_achievements_user_guid'), 'achievements', ['user_guid'], unique=False)

    op.create_table(
        'recommendations',
        sa.Column(
            'guid',
            sa.UUID(as_uuid=False),
            server_default=sa.text('uuid7()'),
            autoincrement=False,
            nullable=False
        ),
        sa.Column('user_guid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.Column('is_neural', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.Column('is_accepted', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.ForeignKeyConstraint(['user_guid'], ['users.guid'], ),
        sa.PrimaryKeyConstraint('guid')
    )
    op.create_index(op.f('ix_recommendations_datetime_create'), 'recommendations', ['datetime_create'], unique=False)
    op.create_index(op.f('ix_recommendations_guid'), 'recommendations', ['guid'], unique=True)
    op.create_index(op.f('ix_recommendations_user_guid'), 'recommendations', ['user_guid'], unique=False)

    op.create_table(
        'schoolchildren_classes',
        sa.Column(
            'guid',
            sa.UUID(as_uuid=False),
            server_default=sa.text('uuid7()'),
            autoincrement=False,
            nullable=False
        ),
        sa.Column('class_guid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('user_guid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('estimation', sa.Float(), nullable=True),
        sa.Column('datetime_estimation_update', sa.DateTime(), nullable=True),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.ForeignKeyConstraint(['class_guid'], ['classes.guid'], ),
        sa.ForeignKeyConstraint(['user_guid'], ['users.guid'], ),
        sa.PrimaryKeyConstraint('guid')
    )
    op.create_index(
        op.f('ix_schoolchildren_classes_class_guid'),
        'schoolchildren_classes',
        ['class_guid'],
        unique=False
    )
    op.create_index(
        op.f('ix_schoolchildren_classes_datetime_create'),
        'schoolchildren_classes',
        ['datetime_create'],
        unique=False
    )
    op.create_index(op.f('ix_schoolchildren_classes_guid'), 'schoolchildren_classes', ['guid'], unique=True)
    op.create_index(op.f('ix_schoolchildren_classes_user_guid'), 'schoolchildren_classes', ['user_guid'], unique=False)

    op.create_table(
        'teacher_classes',
        sa.Column('class_guid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('user_guid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['class_guid'], ['classes.guid'], ),
        sa.ForeignKeyConstraint(['user_guid'], ['users.guid'], ),
        sa.PrimaryKeyConstraint('class_guid', 'user_guid')
    )
    op.create_index(op.f('ix_teacher_classes_class_guid'), 'teacher_classes', ['class_guid'], unique=False)
    op.create_index(op.f('ix_teacher_classes_user_guid'), 'teacher_classes', ['user_guid'], unique=False)

    op.create_table(
        'tests',
        sa.Column(
            'guid',
            sa.UUID(as_uuid=False),
            server_default=sa.text('uuid7()'),
            autoincrement=False,
            nullable=False
        ),
        sa.Column('user_guid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.Column('is_accepted', sa.Boolean(), server_default=sa.text('False'), nullable=False),
        sa.ForeignKeyConstraint(['user_guid'], ['users.guid'], ),
        sa.PrimaryKeyConstraint('guid')
    )
    op.create_index(op.f('ix_tests_datetime_create'), 'tests', ['datetime_create'], unique=False)
    op.create_index(op.f('ix_tests_guid'), 'tests', ['guid'], unique=True)
    op.create_index(op.f('ix_tests_user_guid'), 'tests', ['user_guid'], unique=False)

    op.create_table(
        'answers_tests',
        sa.Column(
            'guid',
            sa.UUID(as_uuid=False),
            server_default=sa.text('uuid7()'),
            autoincrement=False,
            nullable=False
        ),
        sa.Column('test_guid', sa.UUID(as_uuid=False), nullable=False),
        sa.Column('question_id', sa.SmallInteger(), nullable=False),
        sa.Column('score', sa.SmallInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column(
            'datetime_create',
            sa.DateTime(),
            server_default=sa.text("(now() AT TIME ZONE 'Asia/Novosibirsk')"),
            nullable=False
        ),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['test_guid'], ['tests.guid'], ),
        sa.PrimaryKeyConstraint('guid')
    )
    op.create_index(op.f('ix_answers_tests_guid'), 'answers_tests', ['guid'], unique=True)
    op.create_index(op.f('ix_answers_tests_test_guid'), 'answers_tests', ['test_guid'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_answers_tests_test_guid'), table_name='answers_tests')
    op.drop_index(op.f('ix_answers_tests_guid'), table_name='answers_tests')
    op.drop_table('answers_tests')
    op.drop_index(op.f('ix_tests_user_guid'), table_name='tests')
    op.drop_index(op.f('ix_tests_guid'), table_name='tests')
    op.drop_index(op.f('ix_tests_datetime_create'), table_name='tests')
    op.drop_table('tests')
    op.drop_index(op.f('ix_teacher_classes_user_guid'), table_name='teacher_classes')
    op.drop_index(op.f('ix_teacher_classes_class_guid'), table_name='teacher_classes')
    op.drop_table('teacher_classes')
    op.drop_index(op.f('ix_schoolchildren_classes_user_guid'), table_name='schoolchildren_classes')
    op.drop_index(op.f('ix_schoolchildren_classes_guid'), table_name='schoolchildren_classes')
    op.drop_index(op.f('ix_schoolchildren_classes_datetime_create'), table_name='schoolchildren_classes')
    op.drop_index(op.f('ix_schoolchildren_classes_class_guid'), table_name='schoolchildren_classes')
    op.drop_table('schoolchildren_classes')
    op.drop_index(op.f('ix_recommendations_user_guid'), table_name='recommendations')
    op.drop_index(op.f('ix_recommendations_guid'), table_name='recommendations')
    op.drop_index(op.f('ix_recommendations_datetime_create'), table_name='recommendations')
    op.drop_table('recommendations')
    op.drop_index(op.f('ix_achievements_user_guid'), table_name='achievements')
    op.drop_index(op.f('ix_achievements_guid'), table_name='achievements')
    op.drop_index(op.f('ix_achievements_datetime_create'), table_name='achievements')
    op.drop_table('achievements')
    op.drop_index(op.f('ix_users_guid'), table_name='users')
    op.drop_index(op.f('ix_users_datetime_create'), table_name='users')
    op.drop_table('users')
    op.drop_table('questions')
    op.drop_index(op.f('ix_classes_guid'), table_name='classes')
    op.drop_index(op.f('ix_classes_datetime_create'), table_name='classes')
    op.drop_table('classes')
    op.drop_index(op.f('ix_attachments_guid'), table_name='attachments')
    op.drop_table('attachments')
