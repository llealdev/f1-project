WITH results_until_date AS (
    SELECT *
    FROM `student_leal_bronze`.`f1_results`
    WHERE date(date) <= date('2024-04-21')
    ORDER BY date DESC
),
drivers_selected AS (
    SELECT DISTINCT driverid
    FROM results_until_date
    WHERE YEAR >= (
            SELECT MAX(YEAR) - 2
            FROM results_until_date
        )
),
tb_results AS (
    SELECT rsud.*
    FROM results_until_date AS rsud
        INNER JOIN drivers_selected ON drivers_selected.driverid = rsud.driverid
),
tb_life AS (
    SELECT driverid,
        count(DISTINCT YEAR) AS qtd_seasons,
        count(*) AS qtd_sessions,
        SUM(
            CASE
                WHEN (
                    status = 'Finished'
                    OR status LIKE '+%'
                ) THEN 1
                ELSE 0
            END
        ) AS qtd_sesions_fineshed,
        SUM(
            CASE
                WHEN MODE = 'R' THEN 1
                ELSE 0
            END
        ) AS qtd_race,
        SUM(
            CASE
                WHEN MODE = 'R'
                AND (
                    status = 'Finished'
                    OR status LIKE '+%'
                ) THEN 1
                ELSE 0
            END
        ) AS qtd_sesions_fineshed_race,
        SUM(
            CASE
                WHEN MODE = 'S' THEN 1
                ELSE 0
            END
        ) AS qtd_sprint,
        SUM(
            CASE
                WHEN MODE = 'S'
                AND (
                    status = 'Finished'
                    OR status LIKE '+%'
                ) THEN 1
                ELSE 0
            END
        ) AS qtd_sesions_fineshed_sprint,
        SUM(
            CASE
                WHEN position = 1 THEN 1
                ELSE 0
            END
        ) AS qtde_1Pos,
        SUM(
            CASE
                WHEN MODE = 'R' THEN 1
                ELSE 0
            END
        ) AS qtde_1Pos_race,
        SUM(
            CASE
                WHEN MODE = 'S' THEN 1
                ELSE 0
            END
        ) AS qtde_1Pos_Sprint,
        SUM(
            CASE
                WHEN position <= 3 THEN 1
                ELSE 0
            END
        ) AS qtde_podions,
        SUM(
            CASE
                WHEN position <= 3
                AND mode = 'R' THEN 1
                ELSE 0
            END
        ) AS qtde_podions_race,
        SUM(
            CASE
                WHEN position <= 3
                AND mode = 'S' THEN 1
                ELSE 0
            END
        ) AS qtde_podions_sprint,
        SUM(points) AS qtde_points,
        SUM(
            CASE
                WHEN MODE = 'R' THEN points
                ELSE 0
            END
        ) AS qtde_points_race,
        SUM(
            CASE
                WHEN MODE = 'S' THEN points
                ELSE 0
            END
        ) AS qtde_points_sprint,
        AVG(gridposition) AS avg_gridposition,
        AVG(
            CASE
                WHEN MODE = 'R' THEN gridposition
            END
        ) AS avg_gridposition_race,
        AVG(
            CASE
                WHEN MODE = 'S' THEN gridposition
            END
        ) AS avg_gridposition_sprint,
        AVG(position) AS avg_position,
        AVG(
            CASE
                WHEN MODE = 'R' THEN position
            END
        ) AS avg_position_race,
        AVG(
            CASE
                WHEN MODE = 'S' THEN position
            END
        ) AS avg_position_sprint,
        SUM(
            CASE
                WHEN gridposition = 1 THEN 1
                ELSE 0
            END
        ) AS qtd_1_gridposition,
        SUM(
            CASE
                WHEN gridposition = 1
                AND MODE = 'R' THEN 1
                ELSE 0
            END
        ) AS qtd_1_gridposition_race,
        SUM(
            CASE
                WHEN gridposition = 1
                AND MODE = 'S' THEN 1
                ELSE 0
            END
        ) AS qtd_1_gridposition_sprint,
        SUM(
            CASE
                WHEN gridposition = 1
                AND position = 1 THEN 1
                ELSE 0
            END
        ) AS qtd_pole_win,
        SUM(
            CASE
                WHEN gridposition = 1
                AND position = 1
                AND MODE = 'R' THEN 1
                ELSE 0
            END
        ) AS qtd_pole_win_race,
        SUM(
            CASE
                WHEN gridposition = 1
                AND position = 1
                AND MODE = 'S' THEN 1
                ELSE 0
            END
        ) AS qtd_pole_win_sprint,
        SUM(
            CASE
                WHEN points > 0 THEN 1
                ELSE 0
            END
        ) AS qtd_sessions_with_points,
        SUM(
            CASE
                WHEN points > 0
                AND MODE = 'R' THEN 1
                ELSE 0
            END
        ) AS qtd_sessions_with_points_race,
        SUM(
            CASE
                WHEN points > 0
                AND MODE = 'S' THEN 1
                ELSE 0
            END
        ) AS qtd_sessions_with_points_sprint,
        SUM(
            CASE
                WHEN position < gridposition THEN 1
                ELSE 0
            END
        ) AS qtd_sessions_with_points_overtaks,
        SUM(
            CASE
                WHEN position < gridposition
                AND MODE = 'R' THEN 1
                ELSE 0
            END
        ) AS qtd_sessions_with_points_overtaks_race,
        SUM(
            CASE
                WHEN position < gridposition
                AND MODE = 'S' THEN 1
                ELSE 0
            END
        ) AS qtd_sessions_with_points_overtaks_sprint,
        AVG(gridposition - position) AS avg_overtake,
        AVG(
            CASE
                WHEN MODE = 'R' THEN gridposition - position
                ELSE 0
            END
        ) AS avg_overtake_race,
        AVG(
            CASE
                WHEN MODE = 'S' THEN gridposition - position
                ELSE 0
            END
        ) AS avg_overtake_sprint,
        SUM(
            CASE
                WHEN position <= 5 THEN 1
                ELSE 0
            END
        ) AS qtde_pos5,
        SUM(
            CASE
                WHEN position <= 5
                AND mode = 'R' THEN 1
                ELSE 0
            END
        ) AS qtde_pos5_race,
        SUM(
            CASE
                WHEN position <= 5
                AND mode = 'S' THEN 1
                ELSE 0
            END
        ) AS qtde_pos5_sprint,
        SUM(
            CASE
                WHEN gridposition <= 5 THEN 1
                ELSE 0
            END
        ) AS qtde_gridpos5,
        SUM(
            CASE
                WHEN gridposition <= 5
                AND mode = 'R' THEN 1
                ELSE 0
            END
        ) AS qtde_gridpos5_race,
        SUM(
            CASE
                WHEN gridposition <= 5
                AND mode = 'S' THEN 1
                ELSE 0
            END
        ) AS qtde_gridpos5_sprint
    FROM tb_results
    GROUP BY driverid
)
SELECT *
FROM tb_life