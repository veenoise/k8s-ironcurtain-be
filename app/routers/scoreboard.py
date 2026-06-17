from fastapi import APIRouter

from app.database import db
from app.schemas import ScoreboardEntry

router = APIRouter(prefix="/api/v1/scoreboard", tags=["scoreboard"])


@router.get("/", response_model=list[ScoreboardEntry])
async def get_scoreboard():
    users = await db.user.find_many(
        order=[
            {"score": "desc"},
            {"createdAt": "asc"},
        ],
        take=100,
    )
    return [
        ScoreboardEntry(rank=idx + 1, username=u.username, score=u.score)
        for idx, u in enumerate(users)
    ]
