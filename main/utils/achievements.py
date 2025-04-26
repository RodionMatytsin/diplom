from main.models import engine, Achievements, CRUD, SessionHandler
from main.schemas.achievements import AchievementRegular
from uuid import UUID


def serialize_achievement(achievement: Achievements) -> AchievementRegular:
    return AchievementRegular(
        guid=achievement.guid,
        description=achievement.description,
        datetime_create=f"{achievement.datetime_create.strftime('%d.%m.%Y')} в "
                        f"{achievement.datetime_create.strftime('%H:%M')}"
    )


async def get_achievement(
        achievement_guid: UUID | str | None = None,
        user_guid: UUID | str | None = None,
        is_accepted: bool | None = None
) -> tuple[AchievementRegular] | AchievementRegular | tuple:

    where_ = [Achievements.is_deleted == False]
    if achievement_guid is not None:
        where_.append(Achievements.guid == achievement_guid)
    if user_guid is not None:
        where_.append(Achievements.user_guid == user_guid)
    if is_accepted is not None:
        where_.append(Achievements.is_accepted == is_accepted)

    achievements: tuple[Achievements] | Achievements | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).read(
        _where=where_, _all=achievement_guid is None
    )

    if achievements is None or achievements == []:
        return tuple()

    if achievement_guid is None:
        return tuple(serialize_achievement(achievement=achievement) for achievement in achievements)
    return serialize_achievement(achievement=achievements)


async def add_achievement(description: str, user_guid: UUID | str) -> str:

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).create(
        _values=dict(user_guid=user_guid, description=description)
    )

    return "Вы успешно отправили свое новое достижение на модерацию!"
