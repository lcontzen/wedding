drop table if exists invited;
create table invited (
    id integer primary key autoincrement,
    firstname text not null,
    name text not null,
    did_connect boolean,
    party_size integer,
    commune boolean,
    ceremony boolean,
    cocktail boolean,
    dinner boolean,
    party boolean,
    babies boolean
);

drop table if exists replies;
create table replies (
    id integer primary key autoincrement,
    firstname text not null,
    name text not null,
    timestamp datetime default current_timestamp,
    commune boolean,
    ceremony boolean,
    cocktail boolean,
    dinner boolean,
    party boolean,
    babies int,
    comments text,
    filled_in_by text
);

insert into invited (firstname, name, party_size, commune, ceremony, cocktail, dinner, party, babies) 
    values ('laurent', 'contzen', 2, 1, 1, 1, 1, 1, 1);
insert into invited (firstname, name, party_size, commune, ceremony, cocktail, dinner, party, babies)
    values ('a', 'b', 3, 0, 1, 1, 0, 1, 0);
