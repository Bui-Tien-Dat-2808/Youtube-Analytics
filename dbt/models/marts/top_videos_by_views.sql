select
    fv.video_id,
    dc.channel_name,
    fv.publish_date,
    fv.views,
    fv.likes,
    fv.comments
from {{ ref('stg_fact_video') }} as fv
left join {{ ref('stg_dim_channel') }} as dc
    on fv.channel_id = dc.channel_id
order by fv.views desc
limit 20
