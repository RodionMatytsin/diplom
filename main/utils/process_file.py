
async def process_files(content_type_, path_file_, attachment_guid_):
    from main import config, ffmpeg
    import os
    from PIL import Image, ImageOps
    from pillow_heif import register_heif_opener
    from main.models import Attachments, engine, SessionHandler, CRUD
    from uuid_extensions import uuid7

    max_image_size = 1000
    new_path = f'{path_file_.split(".")[0]}{uuid7(as_type="str")}'

    if content_type_ in config.PHOTO_FORMAT:
        new_path += '.jpeg'

        register_heif_opener()
        img = Image.open(path_file_)

        try:
            img = ImageOps.exif_transpose(img)
        except:
            pass

        old_width, old_height = img.size
        if old_width > max_image_size or old_height > max_image_size:
            k_resize = (old_width if old_width > old_height else old_height) / max_image_size
            img = img.resize((int(old_width / k_resize), int(old_height / k_resize)), resample=Image.BILINEAR)

        try:
            img = img.convert('RGB')
        except:
            pass

        img.save(new_path, quality=85, format='JPEG', optimize=True)

    elif content_type_ in config.VIDEO_FORMAT:
        new_path += '.mp4'

        get_new_video_info = ffmpeg.probe(path_file_, cmd=config.FFMPEG + 'ffprobe')

        try:
            old_width = int(get_new_video_info['streams'][0]['width'])
            old_height = int(get_new_video_info['streams'][0]['height'])
        except:
            old_width = int(get_new_video_info['streams'][1]['width'])
            old_height = int(get_new_video_info['streams'][1]['height'])

        if old_width > 1000 or old_height > 1000:
            k_resize = (old_width if old_width > old_height else old_height) / max_image_size
            old_width = int(old_width / k_resize)
            old_height = int(old_height / k_resize)

            ff_input = ffmpeg.input(path_file_)
            ff_video = ff_input.video
            ff_audio = ff_input.audio

            ff_video_scaled = ff_video.filter(
                'scale', width=f'{old_width}', height=f'{old_height}'
            )
            ff_joined = ffmpeg.concat(ff_video_scaled, ff_audio, v=1, a=1).node

            ff_out = ffmpeg.output(ff_joined[0], ff_joined[1], new_path)
            ff_out.run(cmd=config.FFMPEG + 'ffmpeg')
        else:
            ff_input = ffmpeg.input(path_file_)
            ff_video = ff_input.video
            ff_audio = ff_input.audio

            ff_joined = ffmpeg.concat(ff_video, ff_audio, v=1, a=1).node

            ff_out = ffmpeg.output(ff_joined[0], ff_joined[1], new_path)
            ff_out.run(cmd=config.FFMPEG + 'ffmpeg')
    else:
        print("Ну, как так то, некорректный тип")

    if content_type_ in config.PHOTO_FORMAT:
        await CRUD(
            session=SessionHandler.create(engine=engine), model=Attachments
        ).update(
            _where=[Attachments.guid == attachment_guid_], _values=dict(path=new_path, type='image/jpeg')
        )
    else:
        await CRUD(
            session=SessionHandler.create(engine=engine), model=Attachments
        ).update(
            _where=[Attachments.guid == attachment_guid_], _values=dict(path=new_path)
        )

    if path_file_ != new_path:
        os.remove(path_file_)
