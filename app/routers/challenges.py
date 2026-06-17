import hashlib
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.database import db
from app.dependencies import get_current_user
from app.schemas import (
    ChallengeResponse,
    FlagSubmitRequest,
    FlagSubmitResponse,
    QuestionFileResponse,
    QuestionResponse,
)

router = APIRouter(prefix="/api/v1/challenges", tags=["challenges"])

UPLOAD_DIR = "uploads/questions"


def _file_response(f) -> QuestionFileResponse:
    return QuestionFileResponse(
        id=f.id,
        file_name=f.fileName,
        download_url=f"/api/v1/challenges/{f.questionId}/files/{f.id}/download",
    )


@router.get("/", response_model=list[ChallengeResponse])
async def list_challenges(user=Depends(get_current_user)):
    challenges = await db.challenge.find_many(
        include={"questions": {"include": {"files": True}}},
        order={"storyOrder": "asc"},
    )
    result = []
    for c in challenges:
        questions = [
            QuestionResponse(
                id=q.id,
                title=q.title,
                prompt=q.prompt,
                points=q.points,
                files=[_file_response(f) for f in q.files],
            )
            for q in c.questions
        ]
        result.append(
            ChallengeResponse(
                id=c.id,
                name=c.name,
                codename=c.codename,
                description=c.description,
                story_order=c.storyOrder,
                questions=questions,
            )
        )
    return result


@router.post("/submit", response_model=FlagSubmitResponse)
async def submit_flag(body: FlagSubmitRequest, user=Depends(get_current_user)):
    question = await db.question.find_unique(where={"id": body.question_id})
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    existing = await db.submission.find_first(
        where={
            "userId": user.id,
            "questionId": body.question_id,
            "isCorrect": True,
        },
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Flag already submitted for this question",
        )

    if not body.submitted_flag.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Flag cannot be empty",
        )

    flag_hash = hashlib.sha256(body.submitted_flag.encode()).hexdigest()
    is_correct = flag_hash == question.flagHash

    await db.submission.create(
        data={
            "userId": user.id,
            "questionId": body.question_id,
            "isCorrect": is_correct,
        },
    )

    if is_correct:
        await db.user.update(
            where={"id": user.id},
            data={"score": {"increment": question.points}},
        )
        return FlagSubmitResponse(
            correct=True,
            message="Access granted to decrypted files.",
        )

    return FlagSubmitResponse(
        correct=False,
        message="Flag verification failed. Try again.",
    )


@router.get("/{question_id}/files/{file_id}/download")
async def download_file(
    question_id: str,
    file_id: str,
    user=Depends(get_current_user),
):
    file_record = await db.file.find_first(
        where={"id": file_id, "questionId": question_id},
    )
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    if not os.path.isfile(file_record.filePath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server",
        )
    return FileResponse(
        path=file_record.filePath,
        filename=file_record.fileName,
        media_type="application/octet-stream",
    )
