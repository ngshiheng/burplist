SELECT
    product.id,
    platform AS "Platform",
    brand AS "Brand",
    name AS "Product Name",
    quantity AS "Quantity (Unit)",
    url AS "Product Link",
    count(price.product_id) AS "Number of Prices"
FROM
    product
    LEFT JOIN price ON (product.id = price.product_id)
GROUP BY
    product.id
