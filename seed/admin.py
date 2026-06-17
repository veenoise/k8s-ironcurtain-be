import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from app.auth import hash_password
from app.database import db


async def main():
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_username or not admin_password:
        print("ADMIN_USERNAME and ADMIN_PASSWORD must be set in .env")
        return

    await db.connect()

    existing = await db.user.find_unique(where={"username": admin_username})
    if existing:
        print(f"Admin account '{admin_username}' already exists")
    else:
        await db.user.create(
            data={
                "username": admin_username,
                "passwordHash": hash_password(admin_password),
                "role": "admin",
            },
        )
        print(f"Admin account '{admin_username}' created")

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
