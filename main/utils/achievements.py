from main.models import Achievements
from main.schemas.achievements import AchievementRegular
from uuid import UUID


def serialize_achievement(achievement: Achievements) -> AchievementRegular:
    return AchievementRegular(
        achievement_guid=achievement.guid,
        attachment_guid=achievement.attachment_guid,
        description=achievement.description,
        datetime_create=f"{achievement.datetime_create.strftime('%d.%m.%Y')} в "
                        f"{achievement.datetime_create.strftime('%H:%M')}",
        is_accepted=achievement.is_accepted
    )


async def get_achievements(
        achievement_guid: UUID | str | None = None,
        user_guid: UUID | str | None = None,
        is_accepted: bool | None = None
) -> tuple[AchievementRegular] | AchievementRegular | tuple:
    from main.models import engine, CRUD, SessionHandler
    from sqlalchemy import desc

    where_ = [Achievements.is_deleted == False]
    if achievement_guid is not None:
        where_.append(Achievements.guid == achievement_guid)
    if user_guid is not None:
        where_.append(Achievements.user_guid == user_guid)
    if is_accepted is not None:
        where_.append(Achievements.is_accepted == is_accepted)

    achievements: tuple[Achievements] | Achievements | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).extended_query(
        _select=[
            Achievements.guid,
            Achievements.attachment_guid,
            Achievements.description,
            Achievements.datetime_create,
            Achievements.is_accepted
        ],
        _join=[],
        _where=where_,
        _group_by=[],
        _order_by=[desc(Achievements.datetime_create)],
        _all=achievement_guid is None
    )

    if achievements is None or achievements == []:
        return tuple()

    if achievement_guid is None:
        return tuple(serialize_achievement(achievement=achievement) for achievement in achievements)
    return serialize_achievement(achievement=achievements)


async def add_achievement(attachment_guid: UUID | str, description: str, user_guid: UUID | str) -> str:
    from main.models import engine, CRUD, SessionHandler
    from main.utils.files import get_attachment

    current_attachment = await get_attachment(attachment_guid=attachment_guid)
    await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).create(
        _values=dict(user_guid=user_guid, attachment_guid=current_attachment.guid, description=description)
    )

    return "Вы успешно отправили свое новое достижение на модерацию!"
