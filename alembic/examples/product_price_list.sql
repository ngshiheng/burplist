WITH CURRENT_PRICE (product_id, price) AS (
    SELECT
        product_id,
        price
    FROM
        (
            SELECT
                product_id,
                price,
                ROW_NUMBER() OVER (
                    PARTITION BY product_id
                    ORDER BY
                        price.updated_on DESC
                ) AS rownum
            FROM
                price
        ) t
    WHERE
        rownum = 1
),
PREVIOUS_PRICE (product_id, price) AS (
    SELECT
        product_id,
        price,
        updated_on
    FROM
        (
            SELECT
                product_id,
                price,
                updated_on,
                ROW_NUMBER() OVER (
                    PARTITION BY product_id
                    ORDER BY
                        price.updated_on DESC
                ) AS rownum
            FROM
                price
        ) t
    WHERE
        rownum = 2
)
SELECT
    platform AS "Platform",
    name AS "Product Name",
    brand AS "Brand",
    style AS "Style",
    abv AS "ABV (%)",
    volume AS "Volume (mL)",
    curr.price AS "Current ($SGD)",
    prev.price AS "Previous ($SGD)",
    CASE
        WHEN prev.price IS NULL THEN NULL
        ELSE round((curr.price - prev.price) :: numeric, 2)
    END AS "Change ($SGD)",
    quantity AS "Quantity",
    round((curr.price / quantity) :: numeric, 2) AS "Price/Quantity ($SGD)",
    url AS "Product URL",
    TO_CHAR(
        p.updated_on + INTERVAL '8 HOUR',
        'DD-MON-YYYY HH24:MM'
    ) AS "Last Checked",
    TO_CHAR(
        prev.updated_on + INTERVAL '8 HOUR',
        'DD-MON-YYYY HH24:MM'
    ) AS "Last Change"
FROM
    product p
    LEFT JOIN CURRENT_PRICE curr ON curr.product_id = p.id
    LEFT JOIN PREVIOUS_PRICE prev ON prev.product_id = p.id
    AND(prev.price <> curr.price)
