from main import main
from fastapi import UploadFile
from main.schemas.responses import DefaultResponse


@main.get('/api/attachments/{attachment_guid}', status_code=200, tags=["Attachments"], response_model=None)
async def api_get_attachments(attachment_guid: str):
    from main.utils.files import range_requests_response, get_attachment
    attachment = await get_attachment(attachment_guid=attachment_guid)
    return await range_requests_response(file_path=attachment.path, content_type=attachment.type)


@main.post('/api/attachments', status_code=200, tags=["Attachments"], response_model=DefaultResponse)
async def api_post_attachments(file: list[UploadFile], compress: bool = True):
    from main.utils.files import load_and_save_file
    return DefaultResponse(data=await load_and_save_file(file_=file, compress=compress))
