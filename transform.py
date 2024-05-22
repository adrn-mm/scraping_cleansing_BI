#pip install pandas lxml openpyxl
import pandas as pd

#file_path = 'ii04.xls'
file_path='ii16.xls'
# Open file Excel
#read_html returning table value in 2d list
#df = pd.DataFrame(pd.read_excel("ii04.xls",engine='xlrd'))
df = pd.read_html(file_path)

#print(df)
df=df[0]
#print(df.shape)
dr=pd.DataFrame()
amt=pd.DataFrame()
years=pd.DataFrame()
month=pd.DataFrame()
item=pd.DataFrame()
dati=pd.DataFrame()
prov=pd.DataFrame()

#getting modal kerja items
for x in range(18):
 item[x]=df[10:11][3]
 amt[x]=df[10:11][5+x]
 years[x]=df[5:6][5+x]
 month[x]=df[6:7][5+x]
 dati[x]=df[9:10][1]
 prov[x]=df[117:118][1]

#print(amt)

newamt=amt.transpose()
newyears=years.transpose()
newmonth=month.transpose()
newitem=item.transpose()
newdati=dati.transpose()
newprov=prov.transpose()

#print(newmonth)

amt_col=newamt[10].tolist()
years_col=newyears[5].tolist()
month_col=newmonth[6].tolist()
item_col=newitem[10].tolist()
dati_col=newdati[9].tolist()
prov_col=newprov[117].tolist()

dr['Provinsi']=prov_col
dr['Dati II']=dati_col
dr['Item']=item_col
dr['Bulan']=month_col
dr['Tahun']=years_col
dr['Amount']=amt_col


print(dr)
dr.to_excel('result.xlsx', index = False)
