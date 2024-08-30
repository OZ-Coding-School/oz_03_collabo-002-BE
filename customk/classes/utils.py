import uuid

from django.core.files.uploadedfile import UploadedFile

from common.services.ncp_api_conf import ObjectStorage  # Object Storage 클라이언트


def upload_image_to_object_storage(image_file: UploadedFile) -> str:
    if image_file.name is None:
        raise ValueError("Uploaded file does not have a valid name.")

    obj_client = ObjectStorage()
    file_name = f"{uuid.uuid4()}.{image_file.name.split('.')[-1]}"
    bucket_name = "customk-imagebucket"
    object_name = f"class-images/{file_name}"

    status_code, image_url = obj_client.put_object(
        bucket_name, object_name, image_file.read()
    )
    if status_code != 200:
        raise Exception("Failed to upload image to Object Storage")

    return image_url
