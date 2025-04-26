from main import main
from main.schemas.responses import DefaultResponse
from main.schemas.admin.admin import ClassAdd


@main.post('/api/admin/classes', status_code=200, tags=["Admin"], response_model=DefaultResponse)
async def api_admin_create_class(class_add: ClassAdd):
    from main.utils.admin.admin import admin_add_new_class
    return DefaultResponse(message=await admin_add_new_class(name_class=class_add.name_class))
