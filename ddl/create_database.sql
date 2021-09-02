PRAGMA foreign_keys=true;

CREATE TABLE "executed_file" (
	"id"	INTEGER NOT NULL,
	"file"	TEXT NOT NULL UNIQUE,
	"drops"	INTEGER NOT NULL,
	"size"	INTEGER NOT NULL,
	"recorded_at"	NUMERIC NOT NULL,
	"channel"	TEXT NOT NULL,
	"title"	TEXT NOT NULL,
	"channelName"	TEXT NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE "splitted_file" (
	"id"	INTEGER NOT NULL,
	"executed_file_id"	INTEGER NOT NULL,
	"file"	TEXT NOT NULL,
	"size"	INTEGER NOT NULL,
	FOREIGN KEY("executed_file_id") REFERENCES "executed_file"("id"),
	PRIMARY KEY("id")
);
