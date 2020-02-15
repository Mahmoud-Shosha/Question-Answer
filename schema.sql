create table users (
    id serial primary key,
    name text not null,
    password text not null,
    is_expert boolean not null,
    is_admin boolean not null
);

create table questions (
    id serial primary key,
    question text not null,
    answer text,
    asked_by_id integer not null,
    expert_id integer not null
);
