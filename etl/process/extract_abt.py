# %%
import dotenv
import nekt
import os

dotenv.load_dotenv()

# %%
NEKT_TOKEN = os.getenv("NEKT_TOKEN")

nekt.data_access_token = NEKT_TOKEN

# %%
nekt.engine = 'spark'

spark = nekt.get_spark_session()

# %%

(nekt.load_table(layer_name="Silver", table_name="fs_f1_driver_all").createOrReplaceTempView("fs_f1_driver_all"))

(nekt.load_table(layer_name="Silver", table_name="f1_champions").createOrReplaceTempView("f1_champions"))

query = """
SELECT
	driver_all.*,
	coalesce(champions.rankdriver, 0) AS f1champions
FROM
	fs_f1_driver_all AS driver_all
	LEFT JOIN f1_champions AS champions ON driver_all.driverid = champions.DriverId
	AND EXTRACT(YEAR FROM driver_all.dt_ref) = champions.YEAR
WHERE 
	driver_all.dt_ref BETWEEN '2000-01-01' AND '2025-12-31'
"""

# %%
df = spark.sql(query).toPandas()

# %%

df.head()
# %%
df.to_csv("../../data/abt_f1_drivers_champions.csv"
          , index=False
          , sep=";")
# %%
