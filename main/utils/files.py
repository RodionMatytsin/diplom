from typing import BinaryIO
from main.models import Attachments
from fastapi.responses import StreamingResponse
from main.schemas.attachments import AttachmentRegular, AttachmentDefault
from fastapi import UploadFile
from uuid import UUID


async def serialize_attachment(attachment: Attachments) -> AttachmentRegular:
    return AttachmentRegular(
        guid=attachment.guid,
        type=attachment.type,
        url=attachment.url,
        path=attachment.path,
        datetime=attachment.datetime_create
    )


async def get_attachment(attachment_guid: UUID | str) -> Attachments:

    from main.models import engine, SessionHandler, CRUD
    if attachment_guid is not None and len(str(attachment_guid)) < 32:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail={'result': False, 'message': 'Идентификатор указа не корректно', 'data': {}}
        )

    attachment: Attachments | object | None = await CRUD(
        session=SessionHandler.create(engine=engine), model=Attachments
    ).read(
        _where=[Attachments.guid == attachment_guid, Attachments.is_deleted == False],
        _all=False
    )

    if attachment is None:
        attachment: Attachments | object | None = await CRUD(
            session=SessionHandler.create(engine=engine), model=Attachments
        ).read(
            _where=[Attachments.guid == '00000000-0000-0000-0000-000000000000'],
            _all=False
        )

    return attachment


async def get_attachment_with_serialize(attachment_guid: UUID | str) -> AttachmentRegular:
    return await serialize_attachment(attachment=await get_attachment(attachment_guid=attachment_guid))


def _get_range_header(range_header: str, file_size: int) -> tuple[int, int]:
    def _invalid_range():
        from fastapi import HTTPException
        raise HTTPException(
            status_code=416,
            detail={'result': False, 'message': f"Не корректны \"range\" запрос (Range:{range_header!r})", 'data': {}}
        )

    try:
        h = range_header.replace("bytes=", "").split("-")
        start = int(h[0]) if h[0] != "" else 0
        end = int(h[1]) if h[1] != "" else file_size - 1
    except ValueError:
        raise _invalid_range()

    if start > end or start < 0 or end > file_size - 1:
        raise _invalid_range()
    return start, end


def send_bytes_range_requests(
    file_obj: BinaryIO,
    start: int,
    end: int,
    chunk_size: int = 10_000
):
    """Send a file in chunks using Range Requests specification RFC7233

    `start` and `end` parameters are inclusive due to specification
    """
    with file_obj as f:
        f.seek(start)
        while (pos := f.tell()) <= end:
            read_size = min(chunk_size, end + 1 - pos)
            yield f.read(read_size)


async def range_requests_response(file_path: str, content_type: str) -> StreamingResponse:
    import os
    file_size = os.stat(file_path).st_size

    headers = {
        "Content-type": content_type,
        "Accept-ranges": "bytes",
        "Content-encoding": "identity",
        "Content-length": str(file_size)
    }
    start = 0
    end = file_size - 1
    status_code = 200

    return StreamingResponse(
        send_bytes_range_requests(open(file_path, mode="rb"), start, end),
        headers=headers,
        status_code=status_code,
    )


# ниже функции для загрузки и валидации файлов
async def validate_file(file_: list[UploadFile]):
    import magic
    import main.config as config
    from fastapi import HTTPException

    if len(file_) > 1:
        raise HTTPException(406, detail="Получено более одного файла")
    file = file_[0]

    # Получаем file_size
    file_size = file.file.seek(0, 2)
    await file.seek(0)
    if file_size > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail={'result': False, 'message': "Получен большой файл", 'data': {}}
        )

    # Получаем реальный content_type
    real_content_type = magic.from_buffer(file.file.read(2048), mime=True)
    await file.seek(0)

    # Проверяем content_type
    try:
        content_type = file.content_type
    except Exception as e:
        raise HTTPException(
            status_code=415,
            detail={'result': False, 'message': "Тип файла указан не корректно или он вовсе не указан", 'data': {}}
        )

    if real_content_type != content_type:
        # raise HTTPException(
        #     status_code=415,
        #     detail={'result': False, 'message': "Реальный тип файла отличается от передаваемого", 'data': {}}
        # )

        if real_content_type not in config.PHOTO_FORMAT and real_content_type not in config.VIDEO_FORMAT:
            raise HTTPException(
                status_code=415,
                detail={
                    'result': False,
                    'message': f"Получен не корректный формат данных. Допустимые форматы: "
                               f"{config.PHOTO_FORMAT}, {config.VIDEO_FORMAT}",
                    'data': {}
                }
            )
    return file, real_content_type


async def save_file(file_, content_type_):
    import os
    import aiofiles
    from uuid_extensions import uuid7
    import main.config as config

    id_ = uuid7(as_type="str")
    new_name = f'{id_}.{file_.filename.rsplit(".")[-1]}'
    path_file = os.path.join(config.MEDIA_FOLDER, new_name)

    try:
        async with aiofiles.open(path_file, 'wb') as f:
            while contents := file_.file.read(1024 * 1024):
                await f.write(contents)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail={'result': False, 'message': "Произошла ошибка в обработке файла", 'data': {}}
        )
    finally:
        file_.file.close()

    return id_, new_name, path_file, content_type_


async def processed_file(file_, content_type_, compress: bool = True) -> AttachmentDefault:
    from main.models import engine, SessionHandler, CRUD
    from datetime import datetime
    import main.config as config
    from rq import Queue
    import redis

    guid_, new_name_, path_file_, content_type_ = await save_file(file_=file_, content_type_=content_type_)

    await CRUD(
        session=SessionHandler.create(engine=engine), model=Attachments
    ).create(_values=dict(
        guid=guid_,
        type=content_type_,
        url=f'{config.API_MEDIA}{guid_}',
        path=path_file_,
        datetime_create=datetime.now(),
        is_deleted=False
    ))

    if compress:
        # закидываем в очередь файл и обрабатываем его
        # await process_files(content_type_=content_type_, path_file_=path_file_, attachment_id_=id_)
        try:
            from main.utils.process_file import process_files
            q = Queue(name='us_media', connection=redis.Redis(), default_timeout=600000)
            q.enqueue(process_files, args=(content_type_, path_file_, guid_,))
        except Exception as e:
            print(f"Редиска умерла - {e}")

    return AttachmentDefault(
        guid=guid_,
        type=content_type_,
        url=f'{config.API_MEDIA}{guid_}'
    )


async def load_and_save_file(file_: list[UploadFile], compress: bool = True) -> AttachmentDefault:
    file, content_type = await validate_file(file_)
    return await processed_file(file_=file, content_type_=content_type, compress=compress)
