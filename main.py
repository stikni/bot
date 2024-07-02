import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import googlemaps

# Константы
API_KEY = '7138587168:AAFR6IzHBPeq0GVnvAe-0awhFYClKkSs35c'
GMAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'  # Вставьте сюда ваш API ключ Google Maps

# Функция для получения списка квартир с Avito
def get_apartments(city):
    url = f'https://www.avito.ru/{city}/kvartiry/prodam'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    apartments = []
    
    listings = soup.find_all('div', class_='iva-item-content-m2FiN')
    for listing in listings:
        title = listing.find('h3').text.strip()
        link = 'https://www.avito.ru' + listing.find('a')['href']
        price = listing.find('span', class_='price-text-_YGDY').text.strip()
        address = listing.find('span', class_='geo-address-fhHd0').text.strip()
        
        apartments.append({
            'title': title,
            'link': link,
            'price': price,
            'address': address
        })
    
    return apartments

# Функция для расчета расстояния с использованием Google Maps API
def calculate_distance(api_key, origin, destination):
    gmaps = googlemaps.Client(key=api_key)
    distance_result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode='driving')
    distance = distance_result['rows'][0]['elements'][0]['distance']['text']
    return distance

# Функции Telegram бота
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот для поиска квартир на Avito. Используй /search для начала поиска.')

def search_apartments(update: Update, context: CallbackContext) -> None:
    city = 'moskva'  # Здесь можно использовать город, указанный пользователем
    apartments = get_apartments(city)
    
    keyboard = [
        [InlineKeyboardButton("Фильтры", callback_data='filters')],
        [InlineKeyboardButton("Сортировка", callback_data='sort')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    for apartment in apartments:
        update.message.reply_text(
            f"{apartment['title']}\n{apartment['price']}\n{apartment['address']}\n{apartment['link']}",
            reply_markup=reply_markup
        )

def filter_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Фильтры применены")

def sort_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Сортировка применена")

def main() -> None:
    updater = Updater(API_KEY)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("search", search_apartments))
    dispatcher.add_handler(CallbackQueryHandler(filter_callback, pattern='filters'))
    dispatcher.add_handler(CallbackQueryHandler(sort_callback, pattern='sort'))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
