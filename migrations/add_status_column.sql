-- Add status column to receipts table for tracking processing state
-- Migration: add_status_column
-- Date: 2025-12-10

-- Add status column with default value 'pending'
ALTER TABLE receipts 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'pending';

-- Add check constraint to ensure only valid status values
ALTER TABLE receipts
ADD CONSTRAINT receipts_status_check 
CHECK (status IN ('pending', 'processing', 'completed', 'failed'));

-- Create index on status for better query performance when filtering by status
CREATE INDEX IF NOT EXISTS idx_receipts_status ON receipts(status);

-- Update existing records to 'completed' if they have items (backwards compatibility)
-- This assumes that old receipts with data are already completed
UPDATE receipts 
SET status = 'completed' 
WHERE status = 'pending' 
  AND total_amount > 0 
  AND EXISTS (
    SELECT 1 FROM receipt_items WHERE receipt_items.receipt_id = receipts.receipt_id
  );

-- Optional: Add comment to document the column
COMMENT ON COLUMN receipts.status IS 'Processing status: pending (uploaded), processing (extracting), completed (done), failed (error)';
