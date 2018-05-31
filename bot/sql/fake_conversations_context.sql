-- artificial conversations for training
-- conversation 1
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hey', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hi Julian!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('My favorite player is Thomas Müller', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Want to see a video of him?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Yes', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Have you seen this video of Thomas Müller?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thanks', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('You are welcome!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

-- conversation 1
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hey', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hi Julian!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Show me a video of Müller', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Have you seen this video of Thomas Müller?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thanks', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Are you a soccer fan?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Yes', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thats great!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);
