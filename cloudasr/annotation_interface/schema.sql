CREATE TABLE recordings (
	id BLOB PRIMARY KEY ASC,
	model TEXT NOT NULL,
	path TEXT NOT NULL,
	url TEXT NOT NULL,
	hypothesis TEXT NOT NULL,
	confidence REAL NOT NULL,
	created TIMESTAMP CURRENT_TIMESTAMP
);

CREATE TABLE transcriptions (
	recording_id BLOB NOT NULL,
	user_id INTEGER NOT NULL,
	transcription TEXT NOT NULL
);
