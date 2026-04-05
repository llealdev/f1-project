WITH year_driver_points AS (
  SELECT 
    YEAR, 
    DriverId,
    sum(Points) AS TotalPoints
  FROM 
    `student_leal_bronze`.`f1_results`
  WHERE 
    Mode IN ('R', 'S')
  GROUP BY 
    YEAR, 
    DriverId
),
rn_year_driver AS (
  SELECT 
    *, 
    ROW_NUMBER() OVER (PARTITION BY CAST(YEAR AS INT) ORDER BY TotalPoints DESC) AS rankdriver
  FROM 
    year_driver_points
 )

SELECT 
  *
FROM 
  rn_year_driver
WHERE
  rankdriver = 1
ORDER BY 
  YEAR DESC