-- Create receipts table
CREATE TABLE receipts (
    receipt_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    purchase_date TIMESTAMP NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    image_url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create receipt_items table (separate table for the items relationship)
CREATE TABLE receipt_items (
    item_id SERIAL PRIMARY KEY,
    receipt_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER DEFAULT 1,
    category VARCHAR(100) DEFAULT 'other',
    FOREIGN KEY (receipt_id) REFERENCES receipts(receipt_id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_receipts_user_id ON receipts(user_id);
CREATE INDEX idx_receipts_purchase_date ON receipts(purchase_date);
CREATE INDEX idx_receipt_items_receipt_id ON receipt_items(receipt_id);
CREATE INDEX idx_receipt_items_category ON receipt_items(category);