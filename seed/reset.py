import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from app.database import db


async def main():
    await db.connect()

    count = await db.submission.count()
    await db.submission.delete_many()
    print(f"Deleted {count} submissions")

    await db.user.update_many(
        where={},
        data={"score": 0},
    )
    print("All user scores reset to 0")

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
