select
    keyword_name
from {{ source('analytics', 'dim_keyword') }}
