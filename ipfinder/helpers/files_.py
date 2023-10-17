from typing import ByteString, List


async def save_(self, name: str, file: ByteString):
    ...


async def read_(self, name: str) -> List[str]:
    ...
