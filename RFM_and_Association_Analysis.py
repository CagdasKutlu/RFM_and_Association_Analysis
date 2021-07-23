import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

df_ = pd.read_excel("datasets/online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")
df = df_.copy()
df.head()

df.shape
df.dtypes

# Betimsel İstatistikler
df.describe().T

# Eksik Değer Kontrolü
df.isnull().sum()

# Eksik değerlerin veri setinden düşürülmesi
df.dropna(inplace=True)

# Hangi üründen kaç adet var
df["StockCode"].value_counts()

# En çok sipariş edilen ürünler
df.groupby("StockCode").agg({"Quantity":"sum"}).sort_values(by="Quantity",ascending=False).head(5)

# En çok sipariş edilen ürünler
df.groupby("StockCode").agg({"Quantity":"sum"}).sort_values(by="Quantity",ascending=False).head(5)

# Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturuyoruz.
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Recency: Müşteri son alışveriş tarihi - analiz tarihimiz
# Frequency: Eşsiz invoice değerleri
# Monetary: Her bir müşteri için elimizde bulunan toplam kazanç

# Analiz tarihimizi belirliyoruz.
today_date = dt.datetime(2011, 12, 11)
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

#  Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile hesaplayoruz.
#  Hesapladığınız metrikleri "rfm" isimli bir değişkene atadık.
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

#  Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriyoruz.
rfm.columns = ['recency', 'frequency', 'monetary']

#  Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriyoruz.
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm.head()

#  Oluşan 3 farklı değişkenin değerini tek bir değişken olarak ifade ediyoruz ve RFM_SCORE olarak kaydediyoruz.

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str)+
                    rfm['monetary_score'].astype(str))
rfm.head()

# RFM skorlarının segment olarak tanımlanması

# Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlamaları yapacağız.
# Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriyoruz.
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = (rfm['recency_score'].astype(str) +rfm['frequency_score'].astype(str)).replace(seg_map, regex=True)
rfm.head()

# Oluşturduğumuz segmentleri daha iyi gözlemlemek için bir groupby işlemi uyguluyoruz.
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

##################### Elde ettiğimiz skorlara ait bir kaç yorumlama yapalım.  ##########################
#
# Eğer champions hariç. recency değerleri en düşük olan segmentlerden birine bakacak olursak; potential loyalist segmenti
# gözümüze çarpmaktadır. Bu segmentin aynı zamanda müşteri sayısı da fazla olup, frekans ve monetary değerlerine de göz
# atarsak monetary değeri görece yüksek ve gerekli çalışmalarla ve uygun kampanyalarla birlikte frekansı daha da artırıp
# bu segmentteki müşterilerimizle gerekli çalışmaları yapıp. Güzel sonuçlar elde edebiliriz.


# Can't loose segmentimiz oldukça değerli olup sadece uygun indirimler, hediyeler gibi yöntemlerle recency değerini
# azaltabilirsek bu segmentimizle de ilgili güzel sonuçlar elde edebiliriz. Bu sınıfı şirketimize daha çok ilgisini
# çekmeliyiz. Çünkü, çok iyi Frequency ve Monetary değerlerine sahipler biraz daha üstlerine düşmemiz gerekir.

# Promising müşterileri frekans değeri ortalaması 1 olarak gözüküyor. Bu aslında bize bunların elimizden kayıp gitmesinin
# yüksek ihtimal olduğunu ve daha çok denemek için alışveriş yaptıklarını gösterebilir. Recency ortalamasının çok yüksek
# olmaması sebebiyle bu müşterilerden umut kesilmemeli ve çeşitli anketlerle, kendimizi hatırlatmalarla şirketimize
# yönlendirmeliyiz. Çünkü Yeni müşteri bulmak var olan müşteriyi elde tutmaktan daha maliyetlidir!