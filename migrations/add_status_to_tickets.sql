USE tms;

ALTER TABLE tickets
ADD COLUMN status_id INT DEFAULT NULL;

ALTER TABLE tickets
ADD CONSTRAINT fk_tickets_status
FOREIGN KEY (status_id) REFERENCES status(id)
ON DELETE SET NULL;
