-- Drop file_url from questions
ALTER TABLE "questions" DROP COLUMN "file_url";

-- Create files table
CREATE TABLE "files" (
    "id" TEXT NOT NULL,
    "question_id" TEXT NOT NULL,
    "file_name" TEXT NOT NULL,
    "file_path" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "files_pkey" PRIMARY KEY ("id")
);

-- Add foreign key
ALTER TABLE "files" ADD CONSTRAINT "files_question_id_fkey" FOREIGN KEY ("question_id") REFERENCES "questions"("id") ON DELETE CASCADE ON UPDATE CASCADE;
