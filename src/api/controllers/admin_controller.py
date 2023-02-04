import math
import uuid
import datetime

from flask import jsonify, make_response, request

from src.api import  db
from bs4 import BeautifulSoup
import requests
from src.api.auth.auth import requires_auth
from src.api.models import Annonce, Image, Type, ContactInfo, Message, User


def ScrapAnnonce(user):
    if (user.role == "1"):
        return make_response(jsonify({"status": "failed", "data": None, "message": "not admin"}), 401)
    try:
        response = requests.get("http://www.annonce-algerie.com/upload/flux/rss_1.xml", verify=False)
        items = BeautifulSoup(response.content, "xml").find_all("item")
        for item in items:
            response = requests.get(item.find("link").get_text(), verify=False)
            table = BeautifulSoup(response.content, "html.parser").find_all('table', class_="da_rub_cadre")[1].find_all(
                'tr')
            phoneNumberInfo = BeautifulSoup(response.content, "html.parser").find_all('table', class_="da_contact")[
                0].find_all("span", class_="da_contact_value")
            phoneNumber = None
            if len(phoneNumberInfo) != 0:
                phoneNumber = phoneNumberInfo[0].get_text().replace(" ", "").replace("+", "").replace("213",
                                                                                                      "").replace("+33",
                                                                                                                  "0")
            addressInfo = BeautifulSoup(response.content, "html.parser").find_all('table', class_="da_contact")[
                0].find_all("span", class_="da_contact_adr_soc")
            ownerAddress = None
            if len(addressInfo):
                ownerAddress = addressInfo[0].get_text()
            nameInfo = BeautifulSoup(response.content, "html.parser").find_all('table', class_="da_contact")[
                0].find_all("span", class_="da_contact_rais_soc")
            name = None
            if len(nameInfo):
                name = nameInfo[0].get_text()

            data = []
            images = BeautifulSoup(response.content, "html.parser").find_all('table', class_="da_rub_cadre")[
                3].find_all(
                'img')

            for tr in table:
                if len(tr.find_all('td', class_=("da_field_text"))) != 0:
                    data.append(tr.find_all('td', class_=("da_field_text"))[0].get_text())
            category = data[0].split(">")[1].strip()
            if category not in ["Vente", "Echange", "Location", "Location vacances"]:
                continue
            type = data[0].split(">")[2].strip()
            wilaya = data[2].split(">")[1].strip()
            wilaya = wilaya.replace("é", "e")
            wilaya = wilaya.replace("è", "e")
            wilaya = wilaya.replace("à", "a")
            commune = data[2].split(">")[3].strip()
            commune=commune.replace("é", "e")
            commune = commune.replace("è", "e")
            commune = commune.replace("à", "a")
            address = None
            i = 0
            if len(data) == 8:
                i += 1
                address = str(data[3].strip())
            surface = int(data[3 + i].strip().split("m²")[0].strip().replace(" ", ""))
            price = int(str(data[4 + i].split("Dinar")[0].strip()).replace(" ", ""))
            description = data[5 + i].strip()
            date = data[6 + i]
            annonce = createAnnonceFromMap(
                {"type": type.lower(), "wilaya": wilaya, "commune": commune, "surface": surface, "price": price,
                 "description": description, "category": category, "address": address, "date": date,"phoneNumber":phoneNumber,"name":name,"ownerAddress":ownerAddress})
            annonce.add()
            for imageInfo in images:
                image = Image()
                image.annonce_id = annonce.id
                image.link = "http://www.annonce-algerie.com" + imageInfo.get("src")
                image.add()
        return make_response(jsonify({"status":"success","data":None,"message":None}),200)
    except:
        return make_response(jsonify({"status": "failed", "data": None, "message": "problem while scrapping"}),501)


def createAnnonceFromMap(map):
    annonce = Annonce()
    contactInfo = ContactInfo()
    contactInfo.address = map["ownerAddress"]
    contactInfo.phone_number = map["phoneNumber"]
    contactInfo.full_name = map["name"]
    contactInfo.add()
    annonce.id = str(uuid.uuid1())
    annonce.price = map["price"]
    annonce.surface = map["surface"]
    annonce.wilaya = map["wilaya"]
    annonce.commune = map["commune"]
    annonce.category = map["category"]
    annonce.description = map["description"]
    annonce.address = map["address"]
    dates = map["date"].split("/")
    annonce.date = datetime.date(int(dates[2]), int(dates[1]), int(dates[0]) )
    annonce.user_id = None
    annonce.contact_info_id = contactInfo.id
    type = Type.query.filter_by(name=map["type"]).first()
    if type == None:
        type = Type()
        type.name = map["type"]
        type.add()
    annonce.type_id = type.id
    return annonce

def get_website_stats(user):
    if (user.role == "1"):
        return make_response(jsonify({"status": "failed", "data": None, "message": "not admin"}), 401)
    return make_response(jsonify({"data":{"annonces_count":len(Annonce.query.all()),"messages_count":len(Message.query.all()),"users_count":len(User.query.all())},"message":None,"status":"success",}),200)

def get_admin_annonces(user):
    if (user.role == "1"):
        return make_response(jsonify({"status": "failed", "data": None, "message": "not admin"}), 401)
    pageNumber = request.args.get("page", 1, int)

    annonces = Annonce.query.filter_by(user_id=None).paginate(per_page=12,page=pageNumber)
    items = map(lambda annonce: annonce.toJson(), annonces.items)
    return make_response(jsonify({"status": "success", "data": list(items), "message": None, "current_page": pageNumber,
                                  "max_pages": math.ceil(annonces.total / 12)}), 200)


URL = "https://www.beytic.com/annonces-immobilieres/"

strToInt = {"Milliards": 1000000000, "Millions": 1000000}


def getAnnouncesLinks(pageURL):
    """@param pageURL: -all announces- page url
       @return: an array of links that take to the -announce details- page
    """
    html_text = requests.get(pageURL).text
    soup = BeautifulSoup(html_text, "lxml")

    announces_cards = soup.find_all("div", class_=["properties", "properties--management"])

    links = [announce_card.find("a", class_="item-photo")["href"] for announce_card in announces_cards]
    return links


def getPageLink(url, page_number):
    """ @param url: -all announces- page url
        @param page_number : the number of the wanted page starting from 1
        @return: the url of the wanted page
    """
    return f"{url}?_page={page_number}"


def scrap_page(page_url):
    """ @param page_url: url of -all announces- page it contains (cards)
        @return: an array of json objects each object contain the announce details
    """
    announces_links = getAnnouncesLinks(page_url)
    for announce_page_url in announces_links:
        try:
            response = requests.get(announce_page_url)

            soup = BeautifulSoup(response.text, "lxml").find("div", class_="property")

            images = ["https://www.beytic.com/" + img["src"] for img in soup.select("div.slider__img > img")]
            # print("Images :" , *images , sep="\n")

            description = soup.find("div", class_="property__description").select_one("p").text
            # print("Description",description,sep="\n")

            typeAnnonce = soup.find("div", class_="property__ribon").text.strip()
            # print("type :",typeAnnonce,sep="\n")

            surface = soup.find("dd", class_="property__plan-value").text.replace("M²", "").strip()
            # print("surface :",surface)

            priceStr = soup.find("strong", class_="property__price-value").text.strip()

            # print(priceStr)
            price = 0
            if priceStr == "Prix sur demande":
                price = 0
            elif "/M²" in priceStr:
                priceStr.replace("/M²", "")
                priceStr = priceStr.split()
                price = float(priceStr[0]) * strToInt[priceStr[1]] * int(surface)
            else:
                priceStr = priceStr.split()
                price = float(priceStr[0]) * strToInt[priceStr[1]]

            # print("Price :",price,sep="\n")

            property_info_soup = soup.find("div", class_="property__info")

            typeImmoblier = property_info_soup.select_one(".property__info-item:nth-child(1) strong").text
            # print("type immoblier :", typeImmoblier, "\n")

            wilaya, commune = map(str.strip,
                                  property_info_soup.select_one(".property__info-item:nth-child(2)").text.split(","))
            # print("wilaya commune",wilaya,commune,sep="\n")

            params_list_soup = soup.find("ul", class_="property__params-list")

            adresse = params_list_soup.select_one("li:nth-child(1) > strong").text
            date_publication = params_list_soup.select_one("li:nth-child(2) > strong").text

            # print("adresse :",adresse,"date_publication:",date_publication,sep="\n")

            name = BeautifulSoup(response.text, "lxml").select_one(".worker__name > a").text.strip()
            phone_number = BeautifulSoup(response.text, "lxml").select_one(".tel").text.replace("Tel.", "").strip()

            # print("name",name,"phone",phone_number,sep="\n")

            res = {
                "wilaya": wilaya,
                "commune": commune,
                "address": adresse,
                "surface": surface,
                "date": date_publication,
                "prix": price,
                "typeAnnonce": typeAnnonce,
                "typeImmoblier": typeImmoblier,
                "description": description,
                "images": images,
                "contatcatInfo": {
                    "name": name,
                    "picture": None,
                    "email": None,
                    "phoneNumber": phone_number,
                },
                "coordinates": None
            }

            annonce = createAnnonceFromMap(res)
            annonce.add()
            print("added")

            for imageLink in images:
                image = Image()
                image.annonce_id = annonce.id
                image.link = imageLink
                image.add()

            print("added succefully")
        except Exception as e:
            print("exception 133", e)


def scrap_beytic_website(nb_pages_to_scrap):
    """ @param nb_pages_to_scrap: number of pages to scrap
    """
    db.drop_all()
    db.create_all()
    if nb_pages_to_scrap <= 0 or nb_pages_to_scrap > 30: return

    try:
        for page_count in range(1, nb_pages_to_scrap + 1):
            page = getPageLink(URL, page_count)
            scrap_page(page)
            print(f"page {page_count} finished scrapping")

        return make_response(jsonify({"status": "success", "data": None, "message": None}), 200)

    except Exception as e:
        print(e)
        return make_response(jsonify({"status": "failed", "data": None, "message": "problem while scrapping"}), 501)


def createAnnonceFromMap(map):
    annonce = Annonce()
    contactInfo = ContactInfo()
    contactInfo.address = map["contatcatInfo"]["email"]
    contactInfo.phone_number = map["contatcatInfo"]["phoneNumber"]
    contactInfo.full_name = map["contatcatInfo"]["name"]
    contactInfo.add()
    annonce.id = str(uuid.uuid1())
    annonce.price = map["prix"]
    annonce.surface = map["surface"]
    annonce.wilaya = map["wilaya"]
    annonce.commune = map["commune"]
    annonce.category = map["typeAnnonce"]
    annonce.description = map["description"]
    annonce.address = map["address"]
    dates = map["date"].split("-")
    annonce.date = datetime.date(int(dates[2]), int(dates[1]), int(dates[0]))
    annonce.user_id = None
    annonce.contact_info_id = contactInfo.id
    type = Type.query.filter_by(name=map["typeImmoblier"]).first()
    if type == None:
        type = Type()
        type.name = map["typeImmoblier"]
        type.add()
    annonce.type_id = type.id
    return annonce