import time
import logging
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import json

logging.basicConfig(level=logging.INFO)


def handle(msg):
    """
    A function that will be invoked when a message is
    recevied by the bot
    """
    # Get text or data from the message
    text = msg.get("text", None)
    data = msg.get("data", None)
    
    movie_id = 0
    if data is not None:
        # This is a message from a custom keyboard
        chat_id = msg["message"]["chat"]["id"]
        content_type = "data"
    elif text is not None:
        # This is a text message from the user
        chat_id = msg["chat"]["id"]
        content_type = "text"
    else:
        # This is a message we don't know how to handle
        content_type = "unknown"
    
    if content_type == "text":
        message = msg["text"]
        logging.info("Received from chat_id={}: {}".format(chat_id, message))
        
        if message == "/start":
            # Check against the server to see
            # if the user is new or not
            # TODO
            #bot.sendMessage(chat_id, "Welcome!")
            r = requests.post("http://localhost:5000/register", data={'chat_id': chat_id})
            json_data = json.loads(r.text)
            isExist = json_data["exists"]

            if isExist:
                bot.sendMessage(chat_id, "Welcome Back!")
            else:
                bot.sendMessage(chat_id, "Welcome!")

        elif message == "/rate":
            # Ask the server to return a random
            # movie, and ask the user to rate the movie
            # You should send the user the following information:
            # 1. Name of the movie
            # 2. A link to the movie on IMDB
            # TODO
            r = requests.post("http://localhost:5000/get_unrated_movie", data={'chat_id': chat_id})
            json_data = json.loads(r.text)

            movie_id = json_data["id"]
            movie_title = json_data["title"]
            movie_url = json_data["url"]
            msg_temp = "{}: {}".format(movie_title, movie_url)
            bot.sendMessage(chat_id, msg_temp)
            # Create a custom keyboard to let user enter rating
            my_inline_keyboard = [[
                InlineKeyboardButton(text='1', callback_data='{}, {}'.format(1, movie_id)),
                InlineKeyboardButton(text='2', callback_data='{}, {}'.format(2, movie_id)),
                InlineKeyboardButton(text='3', callback_data='{}, {}'.format(3, movie_id)),
                InlineKeyboardButton(text='4', callback_data='{}, {}'.format(4, movie_id)),
                InlineKeyboardButton(text='5', callback_data='{}, {}'.format(5, movie_id))
            ]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=my_inline_keyboard )
            bot.sendMessage(chat_id, "How do you rate this movie?", reply_markup=keyboard)

        elif message == "/recommend":
            # Ask the server to generate a list of
            # recommended movies to the user
            # TODO
            bot.sendMessage(chat_id, "My recommendations:")
            r = requests.post("http://localhost:5000/recommend", data={'chat_id': str(chat_id) ,"top_n": str(3)})

            json_data = json.loads(r.text)
            result_dict = json_data["results"]

            if result_dict:
                for i in result_dict["movies"]:
                    msg_temp = "{}: {}".format(i['title'], i['url'])
                    bot.sendMessage(chat_id, msg_temp)
            else:
                msg_temp = "You have not rated enough movies, we cannot generate recommendation for you"
                bot.sendMessage(chat_id, msg_temp)
        else:
            # Some command that we don't understand
            bot.sendMessage(chat_id, "I don't understand your command.")

    elif content_type == "data":
        # This is data returned by the custom keyboard
        # Extract the movie ID and the rating from the data
        # and then send this to the server
        # TODO
        logging.info("Received rating: {}".format(data))
        bot.sendMessage(chat_id, "Your rating is received!")
        rating, movie_id = [x.strip() for x in data.split(',')]

        r = requests.post("http://localhost:5000/rate_movie", data={'chat_id':str(chat_id), "movie_id": str(movie_id), "rating": rating } ) 
        json_data = json.loads(r.text)
        print(json_data)



if __name__ == "__main__":
    
    # Povide your bot's token 
    bot = telepot.Bot("742559160:AAHw8a__ANT-dOlj4EHVFzHWoOsllVIk9nY")
    MessageLoop(bot, handle).run_as_thread()

    while True:
        time.sleep(10)