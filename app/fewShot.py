examples = [
    {
        "input": "Count unique sessions.", 
        "query": "SELECT COUNT(DISTINCT event_params.value.int_value) AS unique_sessions FROM `lottecard-test.temp_w_ga4.events_`, UNNEST(event_params) AS event_params WHERE event_params.key = 'ga_session_id';"
    },
    {
        "input": "List events by session",
        "query": "SELECT event_name, event_params.value.int_value AS session_id FROM `lottecard-test.temp_w_ga4.events_`, UNNEST(event_params) AS event_params WHERE event_params.key = 'ga_session_id' ORDER BY session_id;",
    },
    {
        "input": "List events by device type",
        "query": "SELECT device.category, ARRAY_AGG(event_name) AS events FROM `lottecard-test.temp_w_ga4.events_` GROUP BY device.category;",
    },
    {
        "input": "Cross-reference user sessions with engagement",
        "query": "SELECT user_pseudo_id, event_name, event_params.value.int_value AS session_id FROM `lottecard-test.temp_w_ga4.events_`, UNNEST(event_params) AS event_params WHERE event_params.key = 'session_engaged' AND event_params.value.int_value = 1;",
    },
    {
        "input": "Track page views and referrers",
        "query": "SELECT event_params.value.string_value AS page_referrer, COUNT(*) AS views FROM `lottecard-test.temp_w_ga4.events_`, UNNEST(event_params) AS event_params WHERE event_params.key = 'page_referrer' GROUP BY page_referrer;",
    }
]