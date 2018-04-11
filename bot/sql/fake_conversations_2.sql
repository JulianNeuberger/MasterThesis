-- artificial conversations for training
-- conversation 1
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hey', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hi Julian!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);
