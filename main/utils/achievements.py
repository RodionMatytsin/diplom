from main.models import engine, Achievements, CRUD, SessionHandler
from main.schemas.achievements import AchievementAdd
from fastapi import HTTPException
from uuid import UUID


async def get_achievement(
        achievement_guid: UUID | str | None = None,
        user_guid: UUID | str | None = None,
        with_exception: bool = False,
        all_: bool = False
) -> tuple[Achievements] | Achievements | None:

    where_ = [Achievements.is_deleted == False]
    if achievement_guid is not None:
        where_.append(Achievements.guid == achievement_guid)
    if user_guid is not None:
        where_.append(Achievements.user_guid == user_guid)

    achievements: tuple[Achievements] | Achievements | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).read(
        _where=where_, _all=all_
    )

    if achievements is None:
        if with_exception:
            raise HTTPException(
                status_code=404,
                detail={'result': False, 'message': 'Достижение не найдено!', 'data': {}}
            )
        return None
    return achievements


async def add_achievement(achievement: AchievementAdd) -> str:

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).create(
        _values=dict(
            user_guid=achievement.user_guid,
            description=achievement.description
        )
    )

    return "Вы успешно отправили свое новое достижение на модерацию!"


async def accept_achievement(achievement_guid: UUID | str):
    await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).update(
        _where=[Achievements.guid == achievement_guid],
        _values=dict(is_accepted=True)
    )


async def reject_achievement(achievement_guid: UUID | str):
    await CRUD(
        session=SessionHandler.create(engine=engine), model=Achievements
    ).update(
        _where=[Achievements.guid == achievement_guid],
        _values=dict(is_deleted=True)
    )