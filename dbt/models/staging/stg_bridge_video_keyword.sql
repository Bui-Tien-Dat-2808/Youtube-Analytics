select
    video_id,
    keyword_name
from {{ source('analytics', 'bridge_video_keyword') }}
