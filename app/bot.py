# Written by Pouya Salehi.
import os
import random
import time
import urllib
import requests
import json
from libraries.panda import *
from libraries.database_man import *

# To check the previous message is being confirmed.
is_in_payment = False
is_in_csv = False
is_in_calc = False

DB_FILE_NAME = "database.db"
ADMINS_GROUP_CHAT_ID = 0  # The admin group chat ID that will be used for messages.
PUBLIC_GROUP_CHAT_ID = 0  # The public group chat ID that will be used for announcements.
BOT_TOKEN = "YOUR BOT TOKEN"
BOT_PUBLIC_URL = "YOUR BOT PUBLIC URL"  # The public url that everyone can send messages to.
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"  # The url which the Python use to interact with the bot API.
FILE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/"
FILE_NAME_CSV = "the_csv.csv"


def prepare_debt_message_for_admins(payer, receivers):
    final_message = f"{payer} :\n "
    for receiver in receivers:
        final_message = final_message + f"{receiver['name']} : {receiver['amount']}\n "
    return final_message


def prepare_debt_message_for_user(username, receivers):
    final_message = f"Yo {username}. You have to pay these guys on poker this time :\n "
    for receiver in receivers:
        final_message = final_message + " "
        final_message = final_message + f"{receiver['amount']} to {receiver['name']} : {receiver['payment_method']}\n"
    return final_message


def not_allowed_private():
    return random.choice(["I'm sorry but I don't give a shit", "Uh huh I am listening..."])


def not_allowed_public():
    return random.choice(['If laughter is the best medicine, your face must be curing the world.', "You're so ugly, you scared the crap out of the toilet.", "No I'm not insulting you, I'm describing you.", "It's better to let someone think you are an Idiot than to open your mouth and prove it.", "If I had a face like yours, I'd sue my parents.", 'Your birth certificate is an apology letter from the condom factory.', 'I guess you prove that even god makes mistakes sometimes.', "The only way you'll ever get laid is if you crawl up a chicken's ass and wait.", "You're so fake, Barbie is jealous.", 'I’m jealous of people that don’t know you!', "My psychiatrist told me I was crazy and I said I want a second opinion. He said okay, you're ugly too.", "You're so ugly, when your mom dropped you off at school she got a fine for littering.", "If I wanted to kill myself I'd climb your ego and jump to your IQ.", "You must have been born on a highway because that's where most accidents happen.", "Brains aren't everything. In your case they're nothing.", "I don't know what makes you so stupid, but it really works.", 'Your family tree must be a cactus because everybody on it is a prick.', 'I can explain it to you, but I can’t understand it for you.', 'Roses are red violets are blue, God made me pretty, what happened to you?', 'Behind every fat woman there is a beautiful woman. No seriously, your in the way.', 'Calling you an idiot would be an insult to all the stupid people.', 'You, sir, are an oxygen thief!', 'Some babies were dropped on their heads but you were clearly thrown at a wall.', "Why don't you go play in traffic.", 'Please shut your mouth when you’re talking to me.', "I'd slap you, but that would be animal abuse.", 'They say opposites attract. I hope you meet someone who is good-looking, intelligent, and cultured.', "Stop trying to be a smart ass, you're just an ass.", 'The last time I saw something like you, I flushed it.', "'m busy now. Can I ignore you some other time?", 'You have Diarrhea of the mouth; constipation of the ideas.', "If ugly were a crime, you'd get a life sentence.", 'Your mind is on vacation but your mouth is working overtime.', 'I can lose weight, but you’ll always be ugly.', "Why don't you slip into something more comfortable... like a coma.", 'Shock me, say something intelligent.', 'If your gonna be two faced, honey at least make one of them pretty.', "Keep rolling your eyes, perhaps you'll find a brain back there.", 'You are not as bad as people say, you are much, much worse.', "Don't like my sarcasm, well I don't like your stupid.", 'Funny insult for being stupid.', "I don't know what your problem is, but I'll bet it's hard to pronounce.", 'You get ten times more girls than me? ten times zero is zero...', 'There is no vaccine against stupidity.', "You're the reason the gene pool needs a lifeguard.", "Sure, I've seen people like you before - but I had to pay an admission.", "How old are you? - Wait I shouldn't ask, you can't count that high.", "Have you been shopping lately? They're selling lives, you should go get one.", "You're like Monday mornings, nobody likes you.", 'Of course I talk like an idiot, how else would you understand me?', 'All day I thought of you... I was at the zoo.', 'To make you laugh on Saturday, I need to you joke on Wednesday.', "You're so fat, you could sell shade.", "I'd like to see things from your point of view but I can't seem to get my head that far up my ass.", "Don't you need a license to be that ugly?", 'My friend thinks he is smart. He told me an onion is the only food that makes you cry, so I threw a coconut at his face.', 'Your house is so dirty you have to wipe your feet before you go outside.', "If you really spoke your mind, you'd be speechless.", 'Stupidity is not a crime so you are free to go.', 'You are so old, when you were a kid rainbows were black and white.', 'If I told you that I have a piece of dirt in my eye, would you move?', 'You so dumb, you think Cheerios are doughnut seeds.', 'So, a thought crossed your mind? Must have been a long and lonely journey.', 'You are so old, your birth-certificate expired.', "Every time I'm next to you, I get a fierce desire to be alone.", "You're so dumb that you got hit by a parked car.", 'Insult about saying something intelligent', "Keep talking, someday you'll say something intelligent!", "You're so fat, you leave footprints in concrete.", 'How did you get here? Did someone leave your cage open?', "Pardon me, but you've obviously mistaken me for someone who gives a damn.", "Wipe your mouth, there's still a tiny bit of bullshit around your lips.", "Don't you have a terribly empty feeling - in your skull?", 'As an outsider, what do you think of the human race?', "Just because you have one doesn't mean you have to act like one.", 'We can always tell when you are lying. Your lips move.', 'Are you always this stupid or is today a special occasion?'])


def calc_finalize(db, data, to_public=False, to_personal=False, in_calc=True):
    final_message_big = "The final calculations are : "
    data_users = fix_multiple(db_to_panda(db, "users"))
    for payer, sub_data in data.items():
        final_message_personal = ""
        payer_row = data_users.loc[data_users["poker_username"] == payer]
        if to_personal:
            try:
                if not payer_row[0]['telegram_username'] == "" and not payer_row[0]['telegram_chat_id'] == "":
                    final_message_personal = f"Dear {payer_row[0]['telegram_username']}. You have to pay total: {sub_data['total']}"
                else:
                    final_message_personal = ""
            except:
                try:
                    if not payer_row['telegram_username'] == "" and not payer_row['telegram_chat_id'] == "":
                        final_message_personal = f"Dear {payer_row['telegram_username']}. You have to pay total: {sub_data['total']}"
                    else:
                        final_message_personal = ""
                except:
                    final_message_personal = ""
                    pass
        final_message_big = final_message_big + f"\n\n\n{payer} has to pay total: {sub_data['total']}:"
        for receiver_name, receiver_data in sub_data['receivers'].items():
            final_message_big = final_message_big + f"\n\nto {receiver_name} ${receiver_data['amount']}\n{receiver_data['payment_method']}"
            if to_personal:
                if not final_message_personal == "" and payer_row is not None:
                    final_message_personal = final_message_personal + f"\nto {receiver_name} ${receiver_data['amount']}"
        if to_personal and not final_message_personal == "":
            send_message(final_message_personal, payer_row['telegram_chat_id'])
    if to_public:
        send_message(final_message_big, PUBLIC_GROUP_CHAT_ID)
    if in_calc:
        send_message(final_message_big + "\n\n\n\n\n/deletecalc to delete the calc data\n\n/group to send the final calcs to the public group only\n\n/personal to send the final calcs to the fellas personal chat only\n\n/toall to send the message to both the public group and the personal data", ADMINS_GROUP_CHAT_ID)


def get_username_from_updates(updates):
    try:
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        return f"@{updates['result'][last_update]['message']['from']['username']}"
    except KeyError:
        return ""


def build_keyboard(items):  # This function is for building buttons for answering such as Yes/No.
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text_privacy(updates):
    allowed_extensions = ["csv", "xls"]
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    privacy = updates["result"][last_update]["message"]["chat"]["type"]
    message_id = updates["result"][last_update]["message"]["message_id"]
    text_message = ""
    file_text = None
    try:
        file_text = updates["result"][last_update]["message"]["document"]["file_id"]
        file_name = updates["result"][last_update]["message"]["document"]["file_name"]
        file_extension = file_name
        while "." in file_extension:
            file_extension = file_extension.split(".", 1)[-1]
        if file_extension in allowed_extensions:
            return text_message, chat_id, privacy, message_id
    except:
        text_message = updates["result"][last_update]["message"]["text"]
    finally:
        return file_text, text_message, chat_id, privacy, message_id


def get_last_chat_update_id(updates):
    last_update = len(updates["result"]) - 1
    return updates["result"][last_update]["update_id"]


def send_message(text, chat_id, replying_to=""):
    # print(f"[!] Sending Message... {chat_id} : {text}")
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&reply_to_message_id={}".format(text, chat_id, replying_to)
    get_url(url)


def echo_all(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        send_message(text, chat)


def get_fileid(updates):
    allowed_extensions = ["csv", "xls"]
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    file_id = updates["result"][last_update]["message"]["document"]["file_id"]
    file_name = updates["result"][last_update]["message"]["document"]["file_name"]
    file_extension = file_name
    while "." in file_extension:
        file_extension = file_extension.split(".", 1)[-1]
    if file_extension in allowed_extensions:
        return file_id


def get_file_path(file_id):
    url_req = URL + f"getFile?file_id={file_id}"
    response = get_json_from_url(url_req)
    return response["result"]["file_path"]


def download_new_csv(file_path):
    if os.path.exists(FILE_NAME_CSV):
        os.remove(FILE_NAME_CSV)
    url_final = FILE_URL + file_path
    r = requests.get(url_final, allow_redirects=True)
    open(FILE_NAME_CSV, "wb").write(r.content)


def main():
    global is_in_payment, is_in_csv, is_in_calc
    print("[!] Clearing up the databases...")
    try:
        get_updates(get_last_chat_update_id(get_updates()))
    except:
        pass
    conn = create_db_connection(True)
    table_check_users(conn)
    table_check_debts(conn)
    init_finish_database_users(conn)
    delete_all_db_debts(conn)
    print("[!] Previous data cleared!\nFetching Google Sheets data from the sheet...")
    sheet_data_to_db(conn, sheets_to_panda())
    close_db_connection(conn)
    print("[+] All DONE! Starting...\n")
    print("[$] The bot is now running!")
    last_text_chat = (None, None, None, None)
    final_calc_data = {}
    while True:
        try:
            updates = get_updates()
            get_updates(get_last_chat_update_id(updates))
            file_text, text, chat, privacy, message_id = get_last_chat_id_and_text_privacy(updates)
            if (file_text, text, chat, message_id) != last_text_chat:
                c = None
                if privacy == "private":
                    c = create_db_connection()
                    # The private messages.
                    username = get_username_from_updates(updates)
                    if not username == "":
                        update_db_users_set_telegram_chat_id(c, (chat, username))
                        update_db_users_set_telegram_username(c, (username, chat))
                    send_message(not_allowed_private(), chat, message_id)
                elif privacy == "supergroup" or privacy == "group":
                    if chat == ADMINS_GROUP_CHAT_ID:
                        # The admin message methods.
                        if is_in_payment:
                            if text == "/confirm" or text == "/confirm@PokerCalcBot":
                                c = create_db_connection()
                                is_in_payment = False
                                reduce_payments_with_csv(c)
                                send_message("Payments are verified!", chat, message_id)
                            elif text == "/deletepayments" or text == "/deletepayments@PokerCalcBot":
                                c = create_db_connection()
                                delete_all_db_debts(c)
                                is_in_payment = False
                                send_message("Early Payments Deleted!", chat, message_id)
                            else:
                                if "@pokercalcbot" in text.lower() or text[0] == "/":
                                    send_message("Invalid Syntax.\n\n/confirm payment data\n\n/deletepayments payment data", chat, message_id)
                        elif is_in_csv:
                            if text == "/confirm" or text == "/confirm@PokerCalcBot":
                                is_in_csv = False
                                send_message("CSV file records are verified!", chat, message_id)
                            elif text == "/deletecsv" or text == "/deletecsv@PokerCalcBot":
                                c = create_db_connection()
                                init_finish_database_users(c)
                                is_in_csv = False
                                send_message("All CSV file records Deleted!", chat, message_id)
                            else:
                                if "@pokercalcbot" in text.lower() or text[0] == "/":
                                    send_message("Invalid Syntax.\n\n/confirm csv data\n\n/deletecsv CSV data", chat, message_id)
                        elif is_in_calc:
                            good_to_go = True
                            if not final_calc_data == {}:
                                if text == "/group" or text == "/group@PokerCalcBot":
                                    c = create_db_connection()
                                    calc_finalize(c, final_calc_data, to_public=True, in_calc=False)
                                    is_in_calc = False
                                elif text == "/personal" or text == "/personal@PokerCalcBot":
                                    c = create_db_connection()
                                    calc_finalize(c, final_calc_data, to_personal=True, in_calc=False)
                                    is_in_calc = False
                                elif text == "/toall" or text == "/toall@PokerCalcBot":
                                    c = create_db_connection()
                                    calc_finalize(c, final_calc_data, to_public=True, to_personal=True, in_calc=False)
                                    is_in_calc = False
                                elif text == "/deletecalc" or text == "/deletecalc@PokerCalcBot":
                                    final_calc_data = {}
                                    good_to_go = False
                                    is_in_calc = False
                                    send_message("Final calculations data deleted.", chat, message_id)
                                else:
                                    good_to_go = False
                                    if "@pokercalcbot" in text.lower() or text[0] == "/":
                                        send_message("Invalid Syntax.\n\n/deletecalc to delete the calc data\n\n/group to send the final calcs to the public group only\n\n/personal to send the final calcs to the fellas personal chat only\n\n/toall to send the message to both the public group and the personal data", chat, message_id)
                                if good_to_go:
                                    is_in_calc = False
                                    send_message("All sent and good to go guyz :D", chat)
                            else:
                                is_in_calc = False
                                send_message("Lol.. How can I send the empty calcs?!\nresetting data bro..", chat, message_id)
                        else:
                            try:
                                c = create_db_connection()
                                file_path = get_file_path(file_text)
                                ext = file_path
                                while "." in ext:
                                    ext = ext.split(".", 1)[-1]
                                if ext == "csv":
                                    download_new_csv(file_path)
                                else:
                                    raise Exception
                                send_message("Please wait while I process the file bro", chat, message_id)
                                csv_to_db(c, FILE_NAME_CSV)
                                # print("SENT TO DB")
                                sheet_data_to_db(c, sheets_to_panda())
                                send_message(get_csv_data(c), chat, message_id)
                                is_in_csv = True
                                is_in_calc = False
                                is_in_payment = False
                            except KeyError or ValueError:
                                line_index = 0
                                for line in text.split('\n'):
                                    if line_index == 1:
                                        break
                                    if not line == "":
                                        if line == "/showcsv" or line == "/showcsv@PokerCalcBot":
                                            c = create_db_connection()
                                            send_message(read_csv_datas(db_to_panda(c, "users")), chat, message_id)
                                        elif line == "/deletecsv" or line == "/deletecsv@PokerCalcBot":
                                            c = create_db_connection()
                                            init_finish_database_users(c)
                                            is_in_csv = False
                                            send_message("All CSV data cleared son", chat, message_id)
                                        elif line == "/deletepayments" or line == "/deletepayments@PokerCalcBot":
                                            c = create_db_connection()
                                            delete_all_db_debts(c)
                                            is_in_payment = False
                                            send_message("All early payment data cleared yo", chat, message_id)
                                        elif line == "/earlypayments" or line == "/earlypayments@PokerCalcBot":
                                            is_in_payment = True
                                            is_in_csv = False
                                            is_in_calc = False
                                            c = create_db_connection()
                                            msg = early_payments(c, text, True)
                                            if "not exists" in msg:
                                                is_in_payment = False
                                                is_in_csv = False
                                                is_in_calc = False
                                            send_message(msg, chat, message_id)  # Give the results for payments.
                                        elif line == "/showpayments" or line == "/showpayments@PokerCalcBot":
                                            c = create_db_connection()
                                            send_message(early_payments(c), chat, message_id)
                                        elif line == "/calc" or line == "/calc@PokerCalcBot":
                                            # print("\nCALCING")
                                            c = create_db_connection()
                                            sheet_data_to_db(c, sheets_to_panda())
                                            final_calc_data = final_calc(c)
                                            # print("\nCALCING1")
                                            calc_finalize(c, final_calc_data, to_public=False, to_personal=False, in_calc=True)
                                            # print("\nCALCING2")
                                            is_in_calc = True
                                            is_in_payment = False
                                            is_in_csv = False
                                        elif line == "/help" or line == "/commands" or line == "/commands@PokerCalcBot" or line == "/help@PokerCalcBot":
                                            send_message("My commands are:\n\n/earlypayments to add early payments\n\n/showpayments to show the given early payments until now\n\n/deletepayments to delete all the given early payment data\n\n/deletecsv to delete all the CSV file datas\n\n/showcsv to show the given CSV files data until now\n\n/calc to do final calulations", chat, replying_to=message_id)
                                        else:
                                            if "@pokercalcbot" in text.lower() or text[0] == "/":
                                                send_message("Invalid syntax. My commands are:\n\n/earlypayments to add early payments\n\n/showpayments to show the given early payments until now\n\n/deletepayments to delete all the given early payment data\n\n/deletecsv to delete all the CSV file datas\n\n/showcsv to show the given CSV files data until now\n\n/calc to do final calulations", chat, replying_to=message_id)
                                        line_index = line_index + 1
                                    else:
                                        continue
                    else:
                        # The public poker group.
                        try:
                            if "@pokercalcbot" in text.lower() or text[0] == "/":
                                send_message(not_allowed_public(), chat, message_id)
                        except:
                            pass
                last_text_chat = file_text, text, chat, message_id
                if c is not None:
                    close_db_connection(c)
        except requests.ConnectionError:
            time.sleep(10)
        except:
            pass
        time.sleep(0.5)


if __name__ == '__main__':
    main()
