"""import requests
from bs4 import BeautifulSoup
import pandas as pd

# Liste pour stocker les données
restaurants = []

# Fonction pour extraire le numéro de téléphone depuis la page détaillée
def extract_phone_from_detail_page(detail_url):
    try:
        response = requests.get(detail_url)
        if response.status_code != 200:
            return "N/A"
        
        soup = BeautifulSoup(response.text, "html.parser")
        phone_area_code = soup.select_one("span.phone-area-code")
        phone_numbers = phone_area_code.find_next("span").text.strip() if phone_area_code else "N/A"
        
        # Combine l'indicatif avec le numéro complet
        return f"({phone_area_code.text.strip()}) {phone_numbers}" if phone_area_code else "N/A"
    except Exception as e:
        print(f"Erreur en accédant à {detail_url}: {e}")
        return "N/A"

# Fonction pour scraper Go Africa Online
def scrape_go_africa(base_url):
    current_page = 1
    while True:
        print(f"Scraping page {current_page} of Go Africa Online...")
        url = f"{base_url}?p={current_page}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Erreur en récupérant la page {current_page}.")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Extraire les informations sur les restaurants
        entries = soup.select("h2.m-0.p-0.leading-none.gap-x-2")  # Nom du restaurant
        for entry in entries:
            name = entry.text.strip()
            facebook = entry.find("a", class_="stretched-link")["href"] if entry.find("a", class_="stretched-link") else None

            # Récupérer le lien vers la page détaillée
            detail_link = entry.find("a", class_="stretched-link")["href"] if entry.find("a", class_="stretched-link") else None
            detail_url = f"https:{detail_link}" if detail_link else None

            # Extraire le numéro de téléphone depuis la page dédiée
            phone = extract_phone_from_detail_page(detail_url) if detail_url else "N/A"

            # Extraire la ville
            parent = entry.find_parent("div", class_="flex-1")
            city_info = parent.find_next("div", class_="flex flex-auto")
            city = city_info.text.strip() if city_info else "N/A"

            restaurants.append({
                "Name": name,
                "Phone": phone,
                "City": city,
                "Facebook": facebook,
                "Source": "Go Africa Online"
            })

        # Vérifier si une page suivante existe
        next_button = soup.select_one("li.next a")
        if not next_button or not next_button["href"]:
            print("Pas de page suivante détectée. Arrêt.")
            break

        current_page += 1

# Fonction pour scraper Le Pratique du Gabon
def scrape_le_pratique(base_url):
    print("Scraping Le Pratique du Gabon...")
    response = requests.get(base_url)
    if response.status_code != 200:
        print("Erreur en récupérant Le Pratique du Gabon.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    entries = soup.select("div.acces")

    for entry in entries:
        name = entry.find("h3").text.strip() if entry.find("h3") else "N/A"
        phone = entry.find("p", class_="portable").text.strip() if entry.find("p", class_="portable") else "N/A"
        city = entry.find("div", class_="adresse").text.strip() if entry.find("div", class_="adresse") else "N/A"

        restaurants.append({
            "Name": name,
            "Phone": phone,
            "City": city,
            "Facebook": None,
            "Source": "Le Pratique du Gabon"
        })

# Appeler les fonctions de scraping
scrape_go_africa("https://www.goafricaonline.com/ga/annuaire/restaurants")
scrape_le_pratique("https://www.lepratiquedugabon.com/rubrique/restaurants/")

# Créer un DataFrame
df = pd.DataFrame(restaurants)

# Ajouter le message personnalisé
if not df.empty:
    df["Personalized Message"] = df.apply(
        lambda row: (
            f"Bonjour {row['Name']},\n"
            f"Nous avons vu que vous êtes référencé sur le site ({row['Source']}).\n"
            f"Nous proposons un service de livraison de bananes plantains en gros, spécifiquement adapté aux besoins des restaurants.\n"
            f"Nous travaillons déjà avec d’autres établissements comme le vôtre pour leur fournir des produits frais et de qualité.\n"
            f"Nous pouvons également livrer d’autres denrées alimentaires sur commande.\n"
            f"Seriez-vous intéressé par une collaboration ?"
        ),
        axis=1
    )

    # Sauvegarder dans un fichier Excel
    output_file = "Restaurants_Gabon_W.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Données sauvegardées dans '{output_file}'.")
else:
    print("Aucune donnée n'a été extraite.")"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Liste pour stocker les données
restaurants = []

# Créer une session
session = requests.Session()

# En-têtes pour simuler un navigateur
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " 
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

# Fonction pour extraire le numéro de téléphone depuis la page détaillée avec BeautifulSoup
def extract_phone_from_detail_page_bs(detail_url):
    try:
        response = session.get(detail_url, headers=headers)
        if response.status_code != 200:
            print(f"Échec de la récupération de la page détaillée: {detail_url}")
            return "N/A"

        soup = BeautifulSoup(response.text, "html.parser")

        # Trouver toutes les balises <a> avec href commençant par 'tel:'
        phone_links = soup.find_all('a', href=re.compile(r'^tel:'))

        if phone_links:
            # Extraire le premier numéro trouvé
            phone_href = phone_links[0]['href']
            # Nettoyer le numéro en retirant 'tel:' et en supprimant les espaces
            phone = phone_href.replace('tel:', '').replace(' ', '').replace('+', '00')  # Remplacer '+' par '00' si nécessaire
            print(f"Numéro extrait via BeautifulSoup pour {detail_url}: {phone}")  # Debug
            return phone
        else:
            # Enregistrer le contenu HTML pour débogage
            page_id = detail_url.split('/')[-1]
            with open(f"page_detail_bs_{page_id}.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            print(f"Élément du téléphone non trouvé pour {detail_url}")
            return "N/A"
    except Exception as e:
        print(f"Erreur en accédant à {detail_url} avec BeautifulSoup: {e}")
        return "N/A"

# Fonction pour scraper Go Africa Online
def scrape_go_africa(base_url):
    current_page = 1
    while True:
        print(f"Scraping page {current_page} de Go Africa Online...")
        url = f"{base_url}?p={current_page}"
        response = session.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Erreur en récupérant la page {current_page}.")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Vérifiez le sélecteur pour les entrées de restaurant
        entries = soup.select("h2.m-0.p-0.leading-none.gap-x-2")  # Remplacez par le sélecteur correct
        if not entries:
            print(f"Aucune entrée trouvée sur la page {current_page}.")
            break

        for entry in entries:
            name = entry.text.strip()
            
            # Supprimer l'extraction de Facebook
            # facebook = entry.find("a", class_="stretched-link")["href"] if entry.find("a", class_="stretched-link") else None

            # Récupérer le lien vers la page détaillée
            detail_link = entry.find("a", class_="stretched-link")["href"] if entry.find("a", class_="stretched-link") else None
            if detail_link and not detail_link.startswith("http"):
                detail_url = f"https:{detail_link}"
            else:
                detail_url = detail_link

            print(f"Restaurant: {name}, Detail URL: {detail_url}")  # Debug

            # Extraire le numéro de téléphone depuis la page dédiée
            phone = extract_phone_from_detail_page_bs(detail_url) if detail_url else "N/A"

            # Extraire la ville
            parent = entry.find_parent("div", class_="flex-1")
            if parent:
                city_info = parent.find_next("div", class_="flex flex-auto")
                city = city_info.text.strip() if city_info else "N/A"
            else:
                city = "N/A"

            restaurants.append({
                "Name": name,
                "Phone": phone,
                "City": city,
                "Source": "Go Africa Online"
            })

            time.sleep(1)  # Délai d'une seconde entre les requêtes

        # Vérifier si une page suivante existe
        next_button = soup.select_one("li.next a")
        if not next_button or not next_button.get("href"):
            print("Pas de page suivante détectée. Arrêt.")
            break

        current_page += 1

# Fonction pour scraper Le Pratique du Gabon
def scrape_le_pratique(base_url):
    print("Scraping Le Pratique du Gabon...")
    response = session.get(base_url, headers=headers)
    if response.status_code != 200:
        print("Erreur en récupérant Le Pratique du Gabon.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    entries = soup.select("div.acces")

    for entry in entries:
        name = entry.find("h3").text.strip() if entry.find("h3") else "N/A"
        phone = entry.find("p", class_="portable").text.strip() if entry.find("p", class_="portable") else "N/A"
        city = entry.find("div", class_="adresse").text.strip() if entry.find("div", class_="adresse") else "N/A"

        restaurants.append({
            "Name": name,
            "Phone": phone,
            "City": city,
            "Source": "Le Pratique du Gabon"
        })

# Appeler les fonctions de scraping
scrape_go_africa("https://www.goafricaonline.com/ga/annuaire/restaurants")
scrape_le_pratique("https://www.lepratiquedugabon.com/rubrique/restaurants/")

# Créer un DataFrame
df = pd.DataFrame(restaurants)

# Fonction pour formater les numéros de téléphone
def format_phone(row):
    phone = row['Phone']
    source = row['Source']
    
    if phone == "N/A":
        return phone
    
    if source == "Go Africa Online":
        # Remplacer '00' par '+' si le numéro commence par '00'
        if phone.startswith('00'):
            return '+' + phone[2:]
        else:
            return phone
    elif source == "Le Pratique du Gabon":
        # Ajouter '+241' et enlever le premier '0'
        if phone.startswith('0'):
            return '+241' + phone[1:]
        else:
            return '+241' + phone
    else:
        return phone

# Appliquer la fonction de formatage
df['Phone'] = df.apply(format_phone, axis=1)

# Ajouter le message personnalisé
if not df.empty:
    df["Personalized Message"] = df.apply(
        lambda row: (
            f"Bonjour {row['Name']},\n"
            f"Nous avons vu que vous êtes référencé sur le site ({row['Source']}).\n"
            f"Nous proposons un service de livraison de bananes plantains en gros, spécifiquement adapté aux besoins des restaurants.\n"
            f"Nous travaillons déjà avec d’autres établissements comme le vôtre pour leur fournir des produits frais et de qualité.\n"
            f"Nous pouvons également livrer d’autres denrées alimentaires sur commande.\n"
            f"Seriez-vous intéressé par une collaboration ?"
        ),
        axis=1
    )

    # Sauvegarder dans un fichier Excel
    output_file = "Restaurants_Gabon_ZC.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Données sauvegardées dans '{output_file}'.")
else:
    print("Aucune donnée n'a été extraite.")
