# %%
import gc
import pandas as pd 
from sklearn import model_selection
from sklearn import ensemble
from sklearn import metrics
from feature_engine import imputation

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

del df 
gc.collect()
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

x_train_transform = missing.fit_transform(x_train)

# %%

clf = ensemble.RandomForestClassifier(
    random_state=42,
    min_samples_leaf=50,
    n_estimators=500,
    n_jobs=4
)

clf.fit(x_train_transform, y_train)

# %%
## Curva roc de treino

y_train_pred = clf.predict(x_train_transform)
y_train_proba = clf.predict_proba(x_train_transform)[:,1]
auc_train = metrics.roc_auc_score(y_train, y_train_proba)
roc_train = metrics.roc_curve(y_train, y_train_proba)
print(f"AUC Train: ", auc_train)

# %%
## Curva roc de test

x_test_transform = missing.fit_transform(x_test)
y_test_pred = clf.predict(x_test_transform)
y_test_proba = clf.predict_proba(x_test_transform)[:,1]
auc_test = metrics.roc_auc_score(y_test, y_test_proba)
roc_test = metrics.roc_curve(y_test, y_test_proba)
print(f"AUC Test: ", auc_test)


# %%
## Curva roc de oot

x_oot_transform = missing.fit_transform(x_oot)
y_oot_pred = clf.predict(x_oot_transform)
y_oot_proba = clf.predict_proba(x_oot_transform)[:,1]
auc_oot = metrics.roc_auc_score(y_oot, y_oot_proba)
roc_oot = metrics.roc_curve(y_oot, y_oot_proba)
print(f"AUC OOT: ", auc_oot)

# %%

import matplotlib.pyplot as plt 

plt.plot(roc_train[0], roc_train[1])
plt.plot(roc_test[0], roc_test[1])
plt.plot(roc_oot[0], roc_oot[1])
plt.legend([f"Treino: {auc_train:.4f}", f"Test: {auc_test:.4f}", f"OOT: {auc_oot:.4f}", ])
plt.grid(True)
plt.title("Curva ROC")

# %%

feature_importances =  pd.Series(clf.feature_importances_, index=x_train_transform.columns)
feature_importances = feature_importances.sort_values(ascending=False)
feature_importances.head(20)
# %%

df_oot['pred'] = y_oot_proba

pd.set_option('display.max_columns', None)

df_oot[['driverid', 'dt_ref', 'f1champions', 'pred']].sort_values(['dt_ref', 'pred'], ascending = False)
# %%
df_oot[['driverid', 'dt_ref', 'f1champions', 'pred']].sort_values(['dt_ref', 'pred'], ascending = False).to_csv("../data/champions_2025.csv", sep=";")

# %%
