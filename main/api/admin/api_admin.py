from main import main
from main.schemas.responses import DefaultResponse
from main.schemas.admin.admin import ClassAdd, ClassDefault
from uuid import UUID


@main.get('/api/admin/classes', status_code=200, tags=["Admin"], response_model=ClassDefault)
async def api_admin_get_classes(class_guid: UUID | str | None = None):
    from main.utils.admin.admin import get_classes_for_admin
    return ClassDefault(data=await get_classes_for_admin(class_guid=class_guid))


@main.post('/api/admin/classes', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_admin_create_class(class_add: ClassAdd):
    from main.utils.admin.admin import admin_add_new_class
    return DefaultResponse(message=await admin_add_new_class(name_class=class_add.name_class))


@main.delete('/api/admin/classes/{class_guid}', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_admin_del_class(class_guid: UUID | str):
    from main.utils.admin.admin import admin_del_class
    return DefaultResponse(message=await admin_del_class(class_guid=class_guid))
