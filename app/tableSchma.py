import json

json_data = """
[{
  "column_name": "event_date",
  "data_type": "STRING"
}, {
  "column_name": "event_timestamp",
  "data_type": "INT64"
}, {
  "column_name": "event_name",
  "data_type": "STRING"
}, {
  "column_name": "event_params",
  "data_type": "ARRAY<STRUCT<key STRING, value STRUCT<string_value STRING, int_value INT64, float_value FLOAT64, double_value FLOAT64>>>"
}, {
  "column_name": "event_previous_timestamp",
  "data_type": "INT64"
}, {
  "column_name": "event_value_in_usd",
  "data_type": "FLOAT64"
}, {
  "column_name": "event_bundle_sequence_id",
  "data_type": "INT64"
}, {
  "column_name": "event_server_timestamp_offset",
  "data_type": "INT64"
}, {
  "column_name": "user_id",
  "data_type": "STRING"
}, {
  "column_name": "user_pseudo_id",
  "data_type": "STRING"
}, {
  "column_name": "privacy_info",
  "data_type": "STRUCT<analytics_storage STRING, ads_storage STRING, uses_transient_token STRING>"
}, {
  "column_name": "user_properties",
  "data_type": "ARRAY<STRUCT<key STRING, value STRUCT<string_value STRING, int_value INT64, float_value FLOAT64, double_value FLOAT64, set_timestamp_micros INT64>>>"
}, {
  "column_name": "user_first_touch_timestamp",
  "data_type": "INT64"
}, {
  "column_name": "user_ltv",
  "data_type": "STRUCT<revenue FLOAT64, currency STRING>"
}, {
  "column_name": "device",
  "data_type": "STRUCT<category STRING, mobile_brand_name STRING, mobile_model_name STRING, mobile_marketing_name STRING, mobile_os_hardware_model STRING, operating_system STRING, operating_system_version STRING, vendor_id STRING, advertising_id STRING, language STRING, is_limited_ad_tracking STRING, time_zone_offset_seconds INT64, browser STRING, browser_version STRING, web_info STRUCT<browser STRING, browser_version STRING, hostname STRING>>"
}, {
  "column_name": "geo",
  "data_type": "STRUCT<city STRING, country STRING, continent STRING, region STRING, sub_continent STRING, metro STRING>"
}, {
  "column_name": "app_info",
  "data_type": "STRUCT<id STRING, version STRING, install_store STRING, firebase_app_id STRING, install_source STRING>"
}, {
  "column_name": "traffic_source",
  "data_type": "STRUCT<name STRING, medium STRING, source STRING>"
}, {
  "column_name": "stream_id",
  "data_type": "STRING"
}, {
  "column_name": "platform",
  "data_type": "STRING"
}, {
  "column_name": "event_dimensions",
  "data_type": "STRUCT<hostname STRING>"
}, {
  "column_name": "ecommerce",
  "data_type": "STRUCT<total_item_quantity INT64, purchase_revenue_in_usd FLOAT64, purchase_revenue FLOAT64, refund_value_in_usd FLOAT64, refund_value FLOAT64, shipping_value_in_usd FLOAT64, shipping_value FLOAT64, tax_value_in_usd FLOAT64, tax_value FLOAT64, unique_items INT64, transaction_id STRING>"
}, {
  "column_name": "items",
  "data_type": "ARRAY<STRUCT<item_id STRING, item_name STRING, item_brand STRING, item_variant STRING, item_category STRING, item_category2 STRING, item_category3 STRING, item_category4 STRING, item_category5 STRING, price_in_usd FLOAT64, price FLOAT64, quantity INT64, item_revenue_in_usd FLOAT64, item_revenue FLOAT64, item_refund_in_usd FLOAT64, item_refund FLOAT64, coupon STRING, affiliation STRING, location_id STRING, item_list_id STRING, item_list_name STRING, item_list_index STRING, promotion_id STRING, promotion_name STRING, creative_name STRING, creative_slot STRING, item_params ARRAY<STRUCT<key STRING, value STRUCT<string_value STRING, int_value INT64, float_value FLOAT64, double_value FLOAT64>>>>>"
}, {
  "column_name": "collected_traffic_source",
  "data_type": "STRUCT<manual_campaign_id STRING, manual_campaign_name STRING, manual_source STRING, manual_medium STRING, manual_term STRING, manual_content STRING, gclid STRING, dclid STRING, srsltid STRING>"
}, {
  "column_name": "is_active_user",
  "data_type": "BOOL"
}]
"""

event_table_info = json.loads(json_data)