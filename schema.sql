create table user (
    id integer primary key autoincrement,
    name text not null,
    password text not null,
    is_expert boolean not null,
    is_admin boolean not null
);

create table question (
    id integer primary key autoincrement,
    question text not null,
    answer text,
    asked_by_id integer not null,
    answered_by_id integer not null
);
