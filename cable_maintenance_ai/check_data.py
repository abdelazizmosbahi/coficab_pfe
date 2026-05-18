import pandas as pd

df = pd.read_csv(r'c:\cable_maintenance_ai\cable_maintenance_ai\feature_extraction\recipe_parameters.csv')

print("Columns:", df.columns.tolist())
print("\nShape:", df.shape)

filtered = df[(df['Machine']=='MC_02') & (df['RecipeId']=='R0001')]
print(f'\nParameters for MC_02 + R0001: {len(filtered)}')

print(f'\nMachines in data: {sorted(df["Machine"].unique())}')
print(f'\nRecipes in data: {sorted(df["RecipeId"].unique())}')

print(f'\nSample machine+recipe combinations:')
combos = df.groupby(['Machine', 'RecipeId']).size().reset_index(name='count')
print(combos.head(20))

if len(filtered) > 0:
    print(f'\nSample parameters for MC_02 + R0001:')
    print(filtered[['Parameter', 'Value', 'ValueMin', 'ValueMean', 'ValueMax']].head(10))
