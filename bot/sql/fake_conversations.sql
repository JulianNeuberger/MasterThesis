-- artificial conversations for training
-- conversation 1
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hey', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hi Julian!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('What can you do?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I can show you news about your favorite players and answer questions about them!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Show me the players you know about.', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I know about Thomas Müller, Cristiano Ronaldo and many more!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('What jerseys do you know?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I know about all kinds of jerseys of Bayern, Juventus and Barca', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Show me a video of Müller', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Do you know this video of Müller?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('i quite enjoyed that video', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('It is really nice you liked it', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Can you show me more of that?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Do you know this video of Thomas Müller already?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('That video was crap', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Too bad you didn''t like that...', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('you are not human, are you?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I am a bot, but I am not planning on taking over the world', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('you are dumb', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Sorry', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('How old is Müller?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Müller is 28 years old.', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Well done', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thank you', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('How many goals did MÜller shoot?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Müller scored 42 times!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thank you', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('You are welcome!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Got to go, bye', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('See you soon!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 1, 0);

-- conversation 2
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hey', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hi Julian!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Are you a bot?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Yes I am a bot!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('What shoes does müller use?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thomas Müller wears the Adidas X 17.1', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('How often did he score?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Müller scored 42 times!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Good job', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thanks', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Have a nice day', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Good bye!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 1, 0);

-- conversation 3
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hi', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hey Julian.', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('What are your abilities?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I can show you news about your favorite players and answer questions about them!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('What jerseys do you have in your database?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I know about all kinds of jerseys of Bayern, Juventus and Barca', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Which players do you know about?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I know about Thomas Müller, Cristiano Ronaldo and many more!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('which shoes are worn by thomas müller?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thomas Müller wears the Adidas X 17.1', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('How old is Müller?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Müller is 28.', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Do you have more videos?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Do you know this video of Thomas Müller already?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('That video was bad', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Too bad you didn''t like that...', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I would like to see another one', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Do you know this video of Thomas Müller already?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('That pic is great!', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I am glad you liked it!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Well done!', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thank you!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('How many times did Müller score?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Müller scored 42 times!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('How old is Müller?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Müller is 28 years old.', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('You are a bot right?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Yes I am a bot!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('you aren''t very smart, are you?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Pardon me...', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('can you tell me which shoes müller uses?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Thomas Müller wears the Adidas X 17.1', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('What players do you know?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I know about Thomas Müller, Cristiano Ronaldo and many more!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('How can you help me?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I can show you news about your favorite players and answer questions about them!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Which jerseys can you show me?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I know about all kinds of jerseys of Bayern, Juventus and Barca', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('See you.', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Bye!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 1, 0);

-- conversation 4
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hi', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Hello Julian!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('are you a robot?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I am a bot, but I am not planning on taking over the world', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('show me a video of MÜller', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Do you know this video of Thomas Müller already?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('That article was interesting!', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('It is great to liked it!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Do you have more videos?', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Do you know this video of Thomas Müller already?', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('I did not like that video at all', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Too bad you didn''t like that...', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('you are stupid', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Excuse me...', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 0, 0);

INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('See you.', datetime('now'), 'Julian', 8, 0, 0, 0);
INSERT INTO turns_sentence (value, said_on, said_by, said_in_id, reward, terminal, used_in_training)
VALUES ('Bye!', datetime('now', '+1 seconds'), 'Chatbot', 8, 1, 1, 0);