-- AlterTable
ALTER TABLE "questions" ADD COLUMN     "file_url" TEXT;

-- AlterTable
ALTER TABLE "users" ADD COLUMN     "role" TEXT NOT NULL DEFAULT 'user';
