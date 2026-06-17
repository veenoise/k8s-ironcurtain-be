import hashlib
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from app.database import db
from app.dependencies import get_admin_user
from app.schemas import (
    ChallengeAdminResponse,
    CreateChallengeRequest,
    QuestionAdminResponse,
    QuestionFileResponse,
    UpdateChallengeRequest,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

UPLOAD_DIR = "uploads/questions"


def _file_response(f) -> QuestionFileResponse:
    return QuestionFileResponse(
        id=f.id,
        file_name=f.fileName,
        download_url=f"/api/v1/challenges/{f.questionId}/files/{f.id}/download",
    )


async def _save_file(question_id: str, file: UploadFile) -> str:
    q_dir = f"{UPLOAD_DIR}/{question_id}"
    os.makedirs(q_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = f"{q_dir}/{unique_name}"
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


@router.post("/challenges", response_model=ChallengeAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    body: CreateChallengeRequest,
    admin=Depends(get_admin_user),
):
    existing = await db.challenge.find_unique(where={"name": body.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Challenge with this name already exists",
        )
    challenge = await db.challenge.create(
        data={
            "name": body.name,
            "codename": body.codename,
            "description": body.description,
            "storyOrder": body.story_order,
        },
    )
    return ChallengeAdminResponse(
        id=challenge.id,
        name=challenge.name,
        codename=challenge.codename,
        description=challenge.description,
        story_order=challenge.storyOrder,
    )


@router.post("/questions", response_model=QuestionAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    title: str = Form(min_length=1, max_length=200),
    prompt: str = Form(min_length=1),
    points: int = Form(ge=0),
    flag: str = Form(min_length=1),
    challenge_id: str = Form(),
    files: list[UploadFile] = File(default=[]),
    admin=Depends(get_admin_user),
):
    challenge = await db.challenge.find_unique(where={"id": challenge_id})
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    flag_hash = hashlib.sha256(flag.encode()).hexdigest()

    question = await db.question.create(
        data={
            "title": title,
            "prompt": prompt,
            "points": points,
            "flagHash": flag_hash,
            "challengeId": challenge_id,
        },
    )

    file_records = []
    for f in files:
        if f.filename:
            file_path = await _save_file(question.id, f)
            record = await db.file.create(
                data={
                    "questionId": question.id,
                    "fileName": f.filename,
                    "filePath": file_path,
                },
            )
            file_records.append(record)

    return QuestionAdminResponse(
        id=question.id,
        title=question.title,
        prompt=question.prompt,
        points=question.points,
        files=[_file_response(f) for f in file_records],
        challenge_id=question.challengeId,
    )


@router.put("/challenges/{challenge_id}", response_model=ChallengeAdminResponse)
async def update_challenge(
    challenge_id: str,
    body: UpdateChallengeRequest,
    admin=Depends(get_admin_user),
):
    challenge = await db.challenge.find_unique(where={"id": challenge_id})
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )
    if body.name is not None and body.name != challenge.name:
        existing = await db.challenge.find_unique(where={"name": body.name})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Challenge with this name already exists",
            )
    data = {k: v for k, v in {
        "name": body.name,
        "codename": body.codename,
        "description": body.description,
        "storyOrder": body.story_order,
    }.items() if v is not None}
    if data:
        challenge = await db.challenge.update(
            where={"id": challenge_id},
            data=data,
        )
    return ChallengeAdminResponse(
        id=challenge.id,
        name=challenge.name,
        codename=challenge.codename,
        description=challenge.description,
        story_order=challenge.storyOrder,
    )


@router.put("/questions/{question_id}", response_model=QuestionAdminResponse)
async def update_question(
    question_id: str,
    title: str | None = Form(default=None, min_length=1, max_length=200),
    prompt: str | None = Form(default=None, min_length=1),
    points: int | None = Form(default=None, ge=0),
    flag: str | None = Form(default=None, min_length=1),
    challenge_id: str | None = Form(default=None),
    files: list[UploadFile] = File(default=[]),
    admin=Depends(get_admin_user),
):
    question = await db.question.find_unique(where={"id": question_id})
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    if challenge_id is not None:
        parent = await db.challenge.find_unique(where={"id": challenge_id})
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found",
            )
    data: dict = {}
    if title is not None:
        data["title"] = title
    if prompt is not None:
        data["prompt"] = prompt
    if points is not None:
        data["points"] = points
    if flag is not None:
        data["flagHash"] = hashlib.sha256(flag.encode()).hexdigest()
    if challenge_id is not None:
        data["challengeId"] = challenge_id
    if data:
        question = await db.question.update(
            where={"id": question_id},
            data=data,
        )

    for f in files:
        if f.filename:
            file_path = await _save_file(question.id, f)
            await db.file.create(
                data={
                    "questionId": question.id,
                    "fileName": f.filename,
                    "filePath": file_path,
                },
            )

    file_records = await db.file.find_many(where={"questionId": question.id})

    return QuestionAdminResponse(
        id=question.id,
        title=question.title,
        prompt=question.prompt,
        points=question.points,
        files=[_file_response(f) for f in file_records],
        challenge_id=question.challengeId,
    )


@router.delete("/questions/{question_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_file(
    question_id: str,
    file_id: str,
    admin=Depends(get_admin_user),
):
    file_record = await db.file.find_first(
        where={"id": file_id, "questionId": question_id},
    )
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    if os.path.isfile(file_record.filePath):
        os.remove(file_record.filePath)
    await db.file.delete(where={"id": file_id})


@router.delete("/challenges/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge(
    challenge_id: str,
    admin=Depends(get_admin_user),
):
    challenge = await db.challenge.find_unique(
        where={"id": challenge_id},
        include={"questions": True},
    )
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )
    for q in challenge.questions:
        q_dir = f"{UPLOAD_DIR}/{q.id}"
        if os.path.isdir(q_dir):
            shutil.rmtree(q_dir)
    await db.challenge.delete(where={"id": challenge_id})


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: str,
    admin=Depends(get_admin_user),
):
    question = await db.question.find_unique(where={"id": question_id})
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    q_dir = f"{UPLOAD_DIR}/{question.id}"
    if os.path.isdir(q_dir):
        shutil.rmtree(q_dir)
    await db.question.delete(where={"id": question_id})
