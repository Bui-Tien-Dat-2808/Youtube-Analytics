select
    publish_date,
    count(*) as video_count
from {{ ref('stg_fact_video') }}
group by publish_date
order by publish_date
