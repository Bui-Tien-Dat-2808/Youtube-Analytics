create schema if not exists analytics;
create schema if not exists staging;
create schema if not exists marts;

create table if not exists analytics.dim_channel (
    channel_id text primary key,
    channel_name text not null
);

create table if not exists analytics.dim_keyword (
    keyword_name text primary key
);

create table if not exists analytics.fact_video (
    video_id text primary key,
    channel_id text not null references analytics.dim_channel(channel_id),
    publish_date date not null,
    views bigint,
    likes bigint,
    comments bigint
);

create table if not exists analytics.bridge_video_keyword (
    video_id text not null references analytics.fact_video(video_id),
    keyword_name text not null references analytics.dim_keyword(keyword_name),
    primary key (video_id, keyword_name)
);
