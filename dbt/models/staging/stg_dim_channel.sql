select
    channel_id,
    channel_name
from {{ source('analytics', 'dim_channel') }}
