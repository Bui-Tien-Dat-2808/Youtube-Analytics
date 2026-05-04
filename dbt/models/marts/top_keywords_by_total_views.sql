select
    bvk.keyword_name,
    count(distinct fv.video_id) as total_videos,
    sum(fv.views) as total_views,
    sum(fv.likes) as total_likes,
    sum(fv.comments) as total_comments
from {{ ref('stg_bridge_video_keyword') }} as bvk
inner join {{ ref('stg_fact_video') }} as fv
    on bvk.video_id = fv.video_id
group by bvk.keyword_name
order by total_views desc
limit 20
