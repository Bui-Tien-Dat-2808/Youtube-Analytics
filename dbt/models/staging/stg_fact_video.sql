select
    video_id,
    channel_id,
    publish_date,
    coalesce(views, 0) as views,
    coalesce(likes, 0) as likes,
    coalesce(comments, 0) as comments
from {{ source('analytics', 'fact_video') }}
