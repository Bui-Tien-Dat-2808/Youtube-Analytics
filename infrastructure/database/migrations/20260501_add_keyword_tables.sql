create table if not exists analytics.dim_keyword (
    keyword_name text primary key
);

create table if not exists analytics.bridge_video_keyword (
    video_id text not null references analytics.fact_video(video_id),
    keyword_name text not null references analytics.dim_keyword(keyword_name),
    primary key (video_id, keyword_name)
);
