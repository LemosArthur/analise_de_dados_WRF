import numpy as np
import pandas as pd
import math

#Abre a planilha com os dados extraídos da rodada WRF
#Nomeia as colunas de acordo com as variáveis extraídas
previsto = pd.read_csv('caminho_para_planilha.csv', 
                  names=['Data', 'VVento 10m (m/s)', 'DirVento 10m (°)',
                        'Temperatura (°C)', 'Umidade Relativa (%)', 'Pressão (hPa)',
                         'Precipitação Acumulada (mm)', 'Radiação (W/m2)'])

#Fixa a quantidade de linhas e colunas que serão mostradas ao chamar os dataframes
pd.set_option('display.max_rows', None, 'display.max_columns', None)

#Reseta os índices, remove a última linha (para que coincida com os horários observados) e remove a coluna das Datas
previsto.reset_index(drop=True, inplace=True)
previsto.drop(previsto.index[600], inplace=True)
previsto.drop(previsto.columns[0],axis = 1, inplace=True)

#Cria a coluna Precipitação Horária(mm) a partir da Precipitação Acumulada (mm)
previsto['Precipitação Horária (mm)'] = previsto['Precipitação Acumulada (mm)'].diff().fillna(value=0)
                     
#Abre a planilha com os dados observados e remove as últimas linhas (para que coincidam com os horários previstos)
observado = pd.read_csv('../observado_inmet.csv', engine = 'python', decimal=',')
observado1 = observado.drop(observado.index[600:])

#Junta os dataframes para filtragem dos dados
df = pd.concat([observado1, previsto], axis=1)

#Remove todas as linhas onde não houverem dados observados
##Isso impossibilita a análise de períodos diferentes de hora em hora
df.dropna(inplace=True)

#Muda o tipo dos dados
df.iloc[:, 2:].astype(float)

#Na coluna Radiação (W/m2), Previsto, muda a unidade de W/m2 para kJ/m2
df.loc[:,'Radiação (W/m2)'] *= 3.6
df.columns['Radiação (W/m2)'] = df.columns['Radiação (kJ/m2)']

#Lista as colunas de interesse
colunas_observado = ['Temp. Ins. (C)', 'Umi. Ins. (%)', 'Pressao Ins. (hPa)', 'Vel. Vento (m/s)', 'Radiacao (KJ/m²)', 'Chuva (mm)']
colunas_previsto = ['Temperatura (°C)', 'Umidade Relativa (%)', 'Pressão (hPa)', 'VVento 10m (m/s)', 'Radiação (kJ/m2)', 'Precipitação Horária (mm)']

#Calcula o coeficiente de correlação de pearson (r)
r = []
for i in range(len(colunas_observado)):                          
    correl = np.corrcoef(df.loc[:, colunas_observado[i]], df.loc[:, colunas_previsto[i]])
    r.append([colunas_previsto[i], correl[1,0]])

correlacoes = pd.DataFrame(r).transpose()


#Calcula o Bias (Desvio Médio)
bias = []
for i in range(len(colunas_observado)):
    bias_calc = np.mean(df.loc[:, colunas_observado[i]] - df.loc[:, colunas_previsto[i]])
    bias.append([colunas_previsto[i], bias_calc])

vies = pd.DataFrame(bias).transpose()

#Calcula o RMSE (Root Mean Squared Error)
rmse = []
for i in range(len(colunas_observado)):
    mse = np.square(np.subtract(df.loc[:, colunas_observado[i]], df.loc[:, colunas_previsto[i]])).mean()                                                     
    rmse_calc = math.sqrt(mse)
    rmse.append([colunas_previsto[i], rmse_calc])
RMSE = pd.DataFrame(rmse).transpose()    

#Termina de configurar o dataframe e cria a planilha final
estatisticas = pd.concat([correlacoes, vies, RMSE])
estatisticas.reset_index(drop=True, inplace=True)
estatisticas.drop(index=[2,4], inplace = True)
estatisticas.reset_index(drop=True, inplace=True)
estatisticas.index = ['id_da_rodada', 'Correlação (r)', 'Bias', 'RMSE']
estatisticas.columns = estatisticas.iloc[0]
estatisticas = estatisticas[1:]
estatisticas.to_csv('caminho_para_planilha_final.csv', sep=' ')