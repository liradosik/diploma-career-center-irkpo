import base64
import uuid

from django.core.files.base import ContentFile


def apply_user_photo_update(request, user):
    previous_photo = user.photo if user.photo else None

    should_remove_photo = request.POST.get('remove_photo') == '1' or request.POST.get('action') == 'remove_photo'
    if should_remove_photo and user.photo:
        user.photo.delete(save=False)
        user.photo = None
        user.save(update_fields=['photo'])
        return

    cropped_photo_data = (request.POST.get('cropped_photo_data') or '').strip()
    uploaded_photo = request.FILES.get('photo')

    if cropped_photo_data.startswith('data:image'):
        try:
            header, encoded = cropped_photo_data.split(';base64,', 1)
            ext = header.split('/')[-1].lower()
            if ext not in {'jpg', 'jpeg', 'png', 'webp'}:
                ext = 'jpg'
            decoded = base64.b64decode(encoded)
            filename = f"avatar_{user.pk}_{uuid.uuid4().hex[:8]}.{ext}"
            user.photo.save(filename, ContentFile(decoded), save=False)
            user.save(update_fields=['photo'])
            if previous_photo and previous_photo.name != user.photo.name:
                previous_photo.delete(save=False)
        except (ValueError, TypeError, base64.binascii.Error):
            return
    elif uploaded_photo:
        user.photo = uploaded_photo
        user.save(update_fields=['photo'])
        if previous_photo and previous_photo.name != user.photo.name:
            previous_photo.delete(save=False)
