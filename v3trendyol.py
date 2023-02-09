import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from math import ceil
from googletrans import LANGUAGES
from googletrans import Translator

translator = Translator()
urls = list()


try:
    with open("fiyatlandırma.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = line[:-1]
            line = line.split(",")

            kargo = float(line[0].split("=")[1])
            kar = float(line[1].split("=")[1])
            komisyon = float(line[2].split("=")[1])
            affiliat = float(line[3].split("=")[1])

    print(f"""
    -------------------------------------------
    Kargo = {kargo}
    Kar = {kar}
    Komisyon = %{komisyon}
    affiliat = %{affiliat}
    -------------------------------------------
    * Üstteki değerlere göre hesaplanacaktır.
    * Değiştirmek isterseniz fiyatlandırma.txt
    dosyası üzerinden değiştirebilirsiniz...
    -------------------------------------------
    """)

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36", 
        "X-Amzn-Trace-Id": "Root=1-6209086d-6b68c17b4f73e9d6174b5736"
    }

    dolar_kuru = input("Güncel dolar kurunu girin(örnek: 14.75): ")

    if("," in dolar_kuru):
        dolar_kuru = dolar_kuru.replace(",", ".")

    dolar_kuru = float(dolar_kuru)

    page_no = int(input("Kaç sayfa ürün çekilecek(1 sayfa = 24 ürün): "))
    excel_file = input("Kaydedilecek dosyanın ismi: ")
    check = int(input("Sayfada kaç adet ürün listeleniyor: "))

    if(page_no * 24 > check):
        page_no = check / 24
        page_no = ceil(page_no)

    print("\n-----------------------------------------------\n")
    print("""Trendyol'da veri çekmek istediğiniz kategoride 
    gerekli filtremeleri yaptıktan sonra url çubuğundaki linki 
    kopyalayıp aşağıdaki "Link" kısmına yapıştırın....
    """)
    print("\n-----------------------------------------------\n")

    time.sleep(1)

    ty_url = input("Link: ")
    print("\n-----------------------------------------------\n")

    if(check >= 25):

        if("&pi=" in ty_url):
            split_url = ty_url.split("&pi=")
            ty_url = split_url[0]
            ty_url = ty_url + "&pi="
        if("?pi=" in ty_url):
            split_url = ty_url.split("?pi=")
            ty_url = split_url[0]
            ty_url = ty_url + "?pi="
        page_counter = 1

        while(page_counter <= page_no):
            ty_url = ty_url + str(page_counter)
            print(f"\n------------------------------\n{ty_url}\n-----------------------\n")
            r = requests.get(ty_url, headers=headers)
            soup = BeautifulSoup(r.content, "lxml")

            catalog = soup.find("div", attrs={"class":"prdct-cntnr-wrppr"})
            products = catalog.find_all("div", attrs={"class":"p-card-wrppr"})

            for url in products:
                url_class = url.find_all("div", attrs={"class":"p-card-chldrn-cntnr"})
                for i in url_class:
                    url_list = i.find_all("a")
                    for k in url_list:
                        end_of_url = k.get("href")
                        url = "https://www.trendyol.com" + end_of_url
                        print(url)
                        urls.append(url)
            if(page_counter >= 10):
                ty_url = list(ty_url)
                ty_url.pop()
                ty_url.pop()
                url_str = ""
                for i in ty_url:
                    url_str += i
                ty_url = url_str

            else:
                ty_url = list(ty_url)
                ty_url.pop()
                url_str = ""
                for i in ty_url:
                    url_str += i
                ty_url = url_str
            page_counter += 1
            print("SAYFA ARTIRILDI...")

    else:
        print(f"\n------------------------------\n{ty_url}\n-----------------------\n")
        r = requests.get(ty_url, headers=headers)
        soup = BeautifulSoup(r.content, "lxml")

        catalog = soup.find("div", attrs={"class":"prdct-cntnr-wrppr"})
        products = catalog.find_all("div", attrs={"class":"p-card-wrppr"})

        for url in products:
            url_class = url.find_all("div", attrs={"class":"p-card-chldrn-cntnr"})
            for i in url_class:
                url_list = i.find_all("a")
                for k in url_list:
                    end_of_url = k.get("href")
                    url = "https://www.trendyol.com" + end_of_url
                    print(url)
                    urls.append(url)

    list_for_excel = list()

    product_counter = 1
    for url in urls:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "lxml")

        print("\n-------------------------------------\n")
        print(product_counter)

        seller = soup.find("a", attrs={"class":"merchant-text"}).getText().strip()
        print(f"SATICI: {seller}")

        title = soup.find("h1", attrs={"class":"pr-new-br"}).getText().strip()

        model_code_list = title.split(" ")
        brand = model_code_list[0]

        if(brand in title):
            title = title.replace(brand, "")

        translated_title = translator.translate(title, src="tr", dest="en").text
        print(f"ÜRÜN ADI: {translated_title}\n")

        print(f"MARKA: {brand}")
        model_code_list.reverse()
        model_code = model_code_list[0]
        print(f"MODEL KODU: {model_code}")

        try:
            price = soup.find("span", attrs={"class":"prc-dsc"}).getText().strip().strip("TL")
        except:
            price = soup.find("span", attrs={"class":"prc-slg"}).getText().strip().strip("TL")

        if("." in price):
            price = price.replace(".", "")
        if("," in price):
            price = price.replace(",", ".")
        print(f"FİYAT: {price}\n")

        price = float(price)
        price = price / dolar_kuru
        ilk_toplam = price + kargo + kar
        komisyon_tutari = ilk_toplam * komisyon / 100
        komisyonlu_toplam = ilk_toplam + (ilk_toplam * komisyon / 100)
        affiliat_tutarı = round(komisyonlu_toplam * affiliat / 100, 4)
        affiliatli_toplam = round(komisyonlu_toplam + (komisyonlu_toplam * affiliat / 100), 2)



        images = soup.find_all("img")
        images.pop(0)
        images.pop()
        main_image = images[0].get("src")
        if("mnresize") in main_image:
            main_image_link_list = main_image.split("/")
            main_image_link_list.pop(3)
            main_image_link_list.pop(3)
            main_image_link_list.pop(3)

            new_main_image_link = ""
            for i in main_image_link_list:
                if(".jpg" in i or ".jpeg" in i):
                    new_main_image_link += i
                else:
                    new_main_image_link += (i + "/")
            main_image = str(new_main_image_link)

        print(f"ANA FOTOĞRAF LİNKİ:\n{main_image}\n")

        print("\n---------------------------\n")

        foto1 = ""
        foto2 = ""
        foto3 = ""
        foto4 = ""
        foto5 = ""
        foto6 = ""
        print("DİĞER FOTOĞRAFLAR\n")

        images.pop(0)
        other_images_list = list()
        for i in images:
            image_link = i.get("src")
            if("wallet-rebate.png" in image_link):
                pass
            else:
                if("mnresize" in image_link):
                    image_link_list = image_link.split("/")
                    image_link_list.pop(3)
                    image_link_list.pop(3)
                    image_link_list.pop(3)

                    new_image_link = ""
                    for i in image_link_list:
                        if(".jpg" in i or ".jpeg" in i):
                            new_image_link += i
                        else:
                            new_image_link += (i + "/")
                    #new_image_link.rstrip("/")
                    print(new_image_link)
                else:
                    new_image_link = image_link
                other_images_list.append(new_image_link)

        try:
            foto1 = other_images_list[0]
        except:
            pass

        try:
            foto2 = other_images_list[1]
        except:
            pass

        try:
            foto3 = other_images_list[2]
        except:
            pass

        try:
            foto4 = other_images_list[3]
        except:
            pass

        try:
            foto5 = other_images_list[4]
        except:
            pass

        try:
            foto6 = other_images_list[5]
        except:
            pass

        print("\n\n")

        print("\nAÇIKLAMALAR\n-------------------")

        product_info = soup.find_all("ul", attrs={"class":"detail-desc-list"})
        description = ""
        for i in product_info:
            description += (i.getText().strip() + "\n")

        filtre1 = "Bu üründen en fazla 10 adet sipariş verilebilir. 10 adetin üzerindeki siparişleri Trendyol iptal etme hakkını saklı tutar."
        filtre2 = "Kampanya fiyatından satılmak üzere 100 adetten fazla stok sunulmuştur."
        filtre3 = "Bir ürün, birden fazla satıcı tarafından satılabilir. Birden fazla satıcı tarafından satışa sunulan ürünlerin satıcıları ürün için belirledikleri fiyata, satıcı puanlarına, teslimat statülerine, ürünlerdeki promosyonlara, kargonun bedava olup olmamasına ve ürünlerin hızlı teslimat ile teslim edilip edilememesine, ürünlerin stok ve kategorileri bilgilerine göre sıralanmaktadır."
        filtre4 = "Ürünlerimiz TRENDYOL etiketi ile gönderilecektir."
        filtre5 = "Kampanya fiyatından satılmak üzere 10 adetten fazla stok sunulmuştur."
        filtre6 = "Bu ürün indirim kampanyasına dahil değildir."
        filtre7 = "İncelemiş olduğunuz ürünün satış fiyatını satıcı belirlemektedir."
        filtre8 = "Listelenen fiyat"
        filtre9 = "tarihine kadar geçerlidir."

        if(filtre1 in description):
            description = description.replace(filtre1, "")

        if(filtre2 in description):
            description = description.replace(filtre2, "")

        if(filtre3 in description):
            description = description.replace(filtre3, "")

        if(filtre4 in description):
            description = description.replace(filtre4, "")

        if(filtre5 in description):
            description = description.replace(filtre5, "")

        if(filtre6 in description):
            description = description.replace(filtre6, "")

        if(filtre7 in description):
            description = description.replace(filtre7, "")

        if(filtre8 in description):
            description = description.replace(filtre8, "")

        if(filtre9 in description):
            description = description.replace(filtre9, "")

        translated_info = "-"
        try:
            translated_info = translator.translate(description, src="tr", dest="en").text
        except:
            pass
        print(translated_info)

        print("\n---------------------------\n")

        product_counter += 1
        
        product_infos = {
            "Link":url,
            "Satıcı":seller,
            "Marka":brand,
            "Ürün Başlığı":translated_title,
            "Model Kodu":model_code,
            "Ürün Açıklaması":translated_info,
            "Ana Fotoğraf":main_image,
            "1. Fotoğraf":foto1,
            "2. Fotoğraf":foto2,
            "3. Fotoğraf":foto3,
            "4. Fotoğraf":foto4,
            "5. Fotoğraf":foto5,
            "6. Fotoğraf":foto6,
            "Ürün Fiyatı":price,
            "Kargo":kargo,
            "Kar":kar,
            "Toplam":ilk_toplam,
            "Komisyon(%)":komisyon,
            "Komisyon Tutarı":komisyon_tutari,
            "Komisyonlu Toplam":komisyonlu_toplam,
            "Affiliat(%)":affiliat,
            "Affiliat Tutarı":affiliat_tutarı,
            "Yüklenecek Fiyat":affiliatli_toplam
        }

        list_for_excel.append(product_infos)

except:
    pass
finally:
    print("\nVeri çekme işlemi tamamlandı...\nÇekilen veriler Excel dosyasına dönüştürülüyor...")

    file_name = excel_file + ".xlsx"

    df_data = pd.DataFrame(list_for_excel)
    df_data.to_excel(file_name, index = False)

    print(f"\n******************************************************\nVeriler {file_name} adlı Excel dosyasına dönüştürüldü...\n*****************************************************\n")

    print("PROGRAM SONLANDI")