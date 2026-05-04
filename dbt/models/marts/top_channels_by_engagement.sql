select
    dc.channel_id,
    dc.channel_name,
    sum(fv.views + fv.likes + fv.comments) as total_engagement,
    count(*) as total_videos
from {{ ref('stg_fact_video') }} as fv
inner join {{ ref('stg_dim_channel') }} as dc
    on fv.channel_id = dc.channel_id
group by dc.channel_id, dc.channel_name
order by total_engagement desc
limit 20
