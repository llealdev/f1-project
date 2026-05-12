# %%
import mlflow

import gc
import pandas as pd 
from sklearn import model_selection
from sklearn import ensemble
from sklearn import metrics
from sklearn import pipeline
from feature_engine import imputation
import matplotlib.pyplot as plt 
import os
import dotenv

dotenv.load_dotenv()

# %% 

MLFLOW_URI = os.getenv("MLFLOW_URI")
mlflow.set_tracking_uri(MLFLOW_URI)

# %% 
mlflow.set_experiment(experiment_id=1)

# %% 


# %%
df = pd.read_csv("../data/abt_f1_drivers_champions.csv", sep=";")
# %%

### SEMMA 

#### SAMPLING 


df["year"] = df["dt_ref"].apply(lambda x: x.split("-")[0]).astype(int)

df_oot = df[df["year"] == 2025].copy()

df_analytics = df[df["year"] < 2025].copy()
# %% 
df_year_round = df_analytics[['year', 'dt_ref']].drop_duplicates()


df_year_round['row_number'] = (df_year_round.sort_values("dt_ref", ascending=False)
                                            .groupby("year")
                                            .cumcount()
                              )

df_year_round[['row_number', 'year', 'dt_ref']]
df_year_round = df_year_round[df_year_round['row_number'] > 4]
df_year_round = df_year_round.drop('row_number', axis=1)


# %%

df_driver_year = df_analytics[["driverid", "year", "f1champions"]].drop_duplicates()
df_driver_year.sort_values(["driverid", "year"], ascending=[True, False])


train, test = model_selection.train_test_split(
        df_driver_year,
        random_state=42,
        train_size=0.8,
        stratify=df_driver_year["f1champions"],
    )

print(f"Taxa de Campeões treino: {train["f1champions"].mean()}")
print(f"Taxa de Campeões test: {test["f1champions"].mean()}")

df_train = train.merge(df_analytics).merge(df_year_round, how='inner')
df_test = test.merge(df_analytics).merge(df_year_round, how='inner')

print(f"Quantidade de linhas treino: {df_train.shape}")
print(f"Quantidade de linhas test: {df_test.shape}")

features = df_train.columns[4:]


x_train, y_train = df_train[features], df_train['f1champions'] 
x_test, y_test = df_test[features], df_test['f1champions']
x_oot, y_oot = df_oot[features], df_oot['f1champions']

del df_year_round, df_analytics
gc.collect()
# %%

#### EXPLORE 
isna = x_train.isna().sum()

# %%
missing = imputation.ArbitraryNumberImputer(
    arbitrary_number=-10000, 
    variables=x_train.columns.tolist()
)


# %%

clf = ensemble.RandomForestClassifier(
    random_state=42,
    min_samples_leaf=50,
    n_estimators=500,
    n_jobs=4
)

model = pipeline.Pipeline(steps=[
    ('Imputation', missing),
    ('RandomForest', clf)
])
# %%
with mlflow.start_run():

    model.fit(x_train, y_train)

    y_train_pred = model.predict(x_train)
    y_train_proba = model.predict_proba(x_train)[:,1]
    ## Curva roc de treino
    auc_train = metrics.roc_auc_score(y_train, y_train_proba)
    roc_train = metrics.roc_curve(y_train, y_train_proba)

    mlflow.log_metric("AUC train", auc_train)
    # mlflow.log_metric("ROC train", roc_train)

    y_test_pred = model.predict(x_test)
    y_test_proba = model.predict_proba(x_test)[:,1]
    ## Curva roc de test
    auc_test = metrics.roc_auc_score(y_test, y_test_proba)
    roc_test = metrics.roc_curve(y_test, y_test_proba)

    mlflow.log_metric("AUC test", auc_test)
    # mlflow.log_metric("ROC test", roc_test)

    y_oot_pred = model.predict(x_oot)
    y_oot_proba = model.predict_proba(x_oot)[:,1]
    auc_oot = metrics.roc_auc_score(y_oot, y_oot_proba)
    roc_oot = metrics.roc_curve(y_oot, y_oot_proba)
    ## Curva roc de OOT
    mlflow.log_metric("AUC OOT", auc_oot)
    # mlflow.log_metric("ROC OOT", roc_oot)

    plt.figure(dpi=200)
    plt.plot(roc_train[0], roc_train[1])
    plt.plot(roc_test[0], roc_test[1])
    plt.plot(roc_oot[0], roc_oot[1])
    plt.legend([f"Treino: {auc_train:.4f}", f"Test: {auc_test:.4f}", f"OOT: {auc_oot:.4f}", ])
    plt.grid(True)
    plt.title("Curva ROC")
    plt.savefig("../data/roc_curve.png")
    mlflow.log_artifact("../data/roc_curve.png")

    feature_importances =  pd.Series(clf.feature_importances_, index=x_train.columns)
    feature_importances = feature_importances.sort_values(ascending=False)
    feature_importances.to_markdown("../data/feature_importance.md")
    mlflow.log_artifact("../data/feature_importance.md")

    model.fit(df[features], df["f1champions"])
    mlflow.sklearn.log_model(model, "model")
# %%
