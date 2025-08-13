import io
import boto3
from config.config import *
from botocore.client import Config


def upload(public_url, file_data, object_key, bucket_name='test'):
    """
    上传文件到 R2 bucket。
    :param public_url: 访问域名
    :param file_data: 文件字节数据或文件路径。
    :param object_key: R2 上的目标路径/文件名。
    :param bucket_name: 桶名称。
    :return: (True, 文件的公共访问链接) 或 (False, None)
    """
    s3 = boto3.client(
        's3',
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4'),
        region_name='auto',
    )

    try:
        if isinstance(file_data, bytes):
            s3.upload_fileobj(io.BytesIO(file_data), bucket_name, object_key)
        elif isinstance(file_data, str):  # assume it's a file path
            s3.upload_file(file_data, bucket_name, object_key)
        else:
            raise ValueError("file_data 必须是字节数据或文件路径。")

        # 使用传入的 public_url 构建最终访问链接
        public_access_url = f"{public_url}/{object_key}"

        return True, public_access_url
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        return False, None
