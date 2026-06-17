from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FlagSubmitRequest(BaseModel):
    question_id: str
    submitted_flag: str = Field(min_length=1)


class FlagSubmitResponse(BaseModel):
    correct: bool
    message: str


class QuestionFileResponse(BaseModel):
    id: str
    file_name: str
    download_url: str


class QuestionResponse(BaseModel):
    id: str
    title: str
    prompt: str
    points: int
    files: list[QuestionFileResponse]


class ChallengeResponse(BaseModel):
    id: str
    name: str
    codename: str
    description: str
    story_order: int
    questions: list[QuestionResponse]


class ScoreboardEntry(BaseModel):
    rank: int
    username: str
    score: int


class CreateChallengeRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    codename: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    story_order: int = Field(ge=0)


class ChallengeAdminResponse(BaseModel):
    id: str
    name: str
    codename: str
    description: str
    story_order: int


class QuestionAdminResponse(BaseModel):
    id: str
    title: str
    prompt: str
    points: int
    files: list[QuestionFileResponse]
    challenge_id: str


class UpdateChallengeRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    codename: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1)
    story_order: int | None = Field(default=None, ge=0)
