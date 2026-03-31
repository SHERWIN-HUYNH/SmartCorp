import hashlib
from typing import BinaryIO


def sha256_from_stream(stream: BinaryIO, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA-256 from a binary stream without loading whole file into memory."""
    digest = hashlib.sha256()

    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        digest.update(chunk)

    return digest.hexdigest()


def sha256_from_file_path(file_path: str, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA-256 from a file path."""
    with open(file_path, "rb") as f:
        return sha256_from_stream(f, chunk_size)


async def sha256_from_upload_file(upload_file, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA-256 from FastAPI UploadFile and reset cursor for later reads."""
    digest = hashlib.sha256()

    await upload_file.seek(0)
    while True:
        chunk = await upload_file.read(chunk_size)
        if not chunk:
            break
        digest.update(chunk)
    await upload_file.seek(0)

    return digest.hexdigest()
