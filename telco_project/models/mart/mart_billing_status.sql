{{
  config(
    materialized='table'
  )
}}

WITH metrics_calculation AS (
    SELECT
        *,
        (COALESCE(payment_date_id, current_date::date) - due_date_id) AS date_diff_days,
        CASE
            WHEN credit_score BETWEEN 0 AND 300 THEN '0-300'
            WHEN credit_score BETWEEN 301 AND 600 THEN '301-600'
            WHEN credit_score BETWEEN 601 AND 900 THEN '601-900'
            ELSE '901-1000'
        END AS score_range,
        CASE
            WHEN invoice_status = 'Paid' AND (payment_date_id - due_date_id) > 0 THEN 'Paid Late'
            WHEN invoice_status = 'Paid' AND (payment_date_id - due_date_id) = 0 THEN 'Paid On Time'
            WHEN invoice_status = 'Paid' AND (payment_date_id - due_date_id) < 0 THEN 'Paid in Advance'
            WHEN invoice_status IN ('Overdue', 'Pending') AND (current_date::date - due_date_id) > 0 THEN 'Overdue'
            WHEN invoice_status IN ('Overdue', 'Pending') AND (current_date::date - due_date_id) = 0 THEN 'Due Today'
            WHEN invoice_status IN ('Overdue', 'Pending') AND (current_date::date - due_date_id) < 0 THEN 'Open'
            ELSE 'Other'
        END AS payment_status
    FROM {{ ref('int_billing_joined_with_dims') }}
),
final_aggregation AS (
    SELECT
        invoice_status,
        payment_status,
        payment_method,
        score_range,
        COUNT(*) AS quantity,
        ROUND(ABS(SUM(total_amount)), 2) AS total_amount,
        ROUND(ABS(SUM(paid_amount)), 2) AS paid_amount,
        ROUND(ABS(SUM(paid_amount) - SUM(total_amount)), 2) AS balance_amount
    FROM metrics_calculation
    GROUP BY
        invoice_status,
        payment_status,
        payment_method,
        score_range
)
SELECT * FROM final_aggregation