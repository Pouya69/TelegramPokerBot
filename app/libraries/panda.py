# This file is working with data on csv files.
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from .database_man import *

GOOGLE_CREDENTIAL_JSON = "credentials.json"
GOOGLE_SHEET_NAME = "botsheet"


def sheets_to_panda():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_CREDENTIAL_JSON, scope)

    gc = gspread.authorize(credentials)

    wks = gc.open(GOOGLE_SHEET_NAME).sheet1

    data = wks.get_all_values()
    headers = data.pop(0)

    df = pd.DataFrame(data, columns=headers)
    return df


def sheet_data_to_db(db, sheet_data):
    db_data = db_to_panda(db, "users2")
    # db_data =
    ll = 1
    for index, row in sheet_data.iterrows():
        row_db = db_data.loc[db_data["player_id"] == row["MEMBER ID #"]]
        if not row_db.empty:
            if not row_db["player_id"].item() == "":
                update_db_users_2(db, (row["PLAYER HANDLE"], row["TELEGRAM USERNAME"], f"Venmo : {'https://venmo.com/' + row['VENMO ID'] if not row['VENMO ID'] == '' else ''}\nCashApp : {'https://cash.app/' + row['CASHAPP'] if not row['CASHAPP'] == '' else ''}\nZelle : {row['ZELLE']}\nPayPal : {row['PAYPAL']}", row["MEMBER ID #"]))
            else:
                # print("INSERTING")
                insert_db_users(db, (row["MEMBER ID #"], row["PLAYER HANDLE"], row["TELEGRAM USERNAME"], "", f"Venmo : {'https://venmo.com/' + row['VENMO ID'] if not row['VENMO ID'] == '' else ''}\nCashApp : {'https://cash.app/' + row['CASHAPP'] if not row['CASHAPP'] == '' else ''}\nZelle : {row['ZELLE']}\nPayPal : {row['PAYPAL']}", 0.0))
        else:
            insert_db_users(db, (row["MEMBER ID #"], row["PLAYER HANDLE"], row["TELEGRAM USERNAME"], "", f"Venmo : {'https://venmo.com/' + row['VENMO ID'] if not row['VENMO ID'] == '' else ''}\nCashApp : {'https://cash.app/' + row['CASHAPP'] if not row['CASHAPP'] == '' else ''}\nZelle : {row['ZELLE']}\nPayPal : {row['PAYPAL']}", 0.0))
        # print(f"\nCAT {row_db['player_id'][0]}\n")

    # print(sheet_data["PLAYER HANDLE"][int(sheet_data["#"])-1])


def read_data(file_name):
    return pd.read_csv(file_name, delimiter=";")


def db_to_panda(db, table_name):
    if table_name == "users":
        data = pd.read_sql_query(f"SELECT * FROM users WHERE profit != 0", db)
        return data
    if table_name == "users2":
        data = pd.read_sql_query(f"SELECT * FROM users", db)
        return data
    elif table_name == "debts":
        data = pd.read_sql_query(f"SELECT * FROM debts WHERE amount != 0", db)  # We should use row['name'].item() to get the value for it
        return data


def read_csv_datas(data):
    final_message = "The given CSV data are:\n"
    if not data.empty:
        data = fix_multiple(data)
        for index, row in data.iterrows():
            if not row['profit'] == 0:
                final_message = final_message + f"\n{row['poker_username']} has {row['profit']}"
    final_message = final_message + "\n\n/deletecsv to delete CSV data"
    return final_message


def fix_multiple(df):
    return df.drop_duplicates(subset=["poker_username", "telegram_username", "telegram_chat_id", "payment_link", "profit"])


def csv_to_db(db, file_name):
    data = read_data(file_name)
    for index, row in data.iterrows():
        player_id = row["ID"]
        profit = float(row["Profit"])
        try:
            d = select_one_db_users(db, player_id)
            if not d[1] == "":
                update_db_users_unique(db, (player_id, d[6] + profit, player_id))
            else:
                insert_db_users(db, (player_id, player_id, "", "", "", profit))
        except TypeError:
            insert_db_users(db, (player_id, player_id, "", "", "", profit))


def get_csv_data(db):
    final_message = "The CSV data yet :\n\n"
    for row in select_all_db_users(db):
        profit = float(row[6])
        if not profit == 0:
            final_message = final_message + f"\n{row[2]} has {profit}"
    return final_message + "\n\nDo you confirm?\n/confirm\n\n/deletecsv"


def profits_fixed(df):  # This function returns the data with profits merged for users with different ID but same name.
    # Note that we do not need other things in it. We just need the Player with Profit.
    return df.groupby(["poker_username", "telegram_username", "telegram_chat_id", "payment_link"], as_index=False).sum().sort_values('profit')
    # return df.groupby(["Player"], as_index=False).agg({'Profit': 'sum'})


def get_telegram_chat_id(db, player_id, telegram_username):
    result = ""
    if player_id == "":
        result = select_one_db_users_telegram(db, telegram_username)[4]
    else:
        result = select_one_db_users(db, player_id)[4]
    return int(result)


def early_payments(db, p="", insert=False):
    # p = "/earlypayments\n\nali  adppa s paid cat 100\ncat paid gta 200\ncat paid gta 22222222"
    result = "The given early payments until now are :\n"
    delete_part = "/earlypayments\n"
    separator = " paid "
    p = p.replace(delete_part, "")
    if insert:
        for line in p.split('\n'):
            if not line == "":
                if separator in line:
                    try:
                        amount = line.split(" ")[-1]
                        payer = line.split(separator, 1)[0]
                        receiver = line.split(separator, 1)[1].split(" " + amount, 1)[0]
                        try:
                            lt = select_one_db_users_handle(db, payer)
                            if lt[1] == "":
                                raise Exception
                        except:
                            return f"The payer name {payer} not exists\n/delete to delete early payments"
                        try:
                            lt2 = select_one_db_users_handle(db, receiver)
                            if lt2[1] == "":
                                raise Exception
                        except:
                            return f"The receiver name {receiver} not exists\n/delete to delete early payments"
                        try:
                            float(amount)
                        except:
                            return "The amount is not a number.\n/delete to delete early payments"
                        insert_db_debts(db, (payer, receiver, float(amount)))
                    except ValueError:
                        continue
    for row in select_all_db_debts(db):
        result = result + "\n"
        result = result + f"{str(row[0])}: {row[1]} paid {row[2]} {str(row[3])}"
    if insert:
        result = result + "\n\nDo you confirm?\n/confirm OR /deletepayments"
    else:
        result = result + "\n\n/deletepayments to delete them."
    return result


def reduce_payments_with_csv(db):
    # 1 -> payer
    # 2 -> receiver
    # 3 -> amount
    #for cs in csv_rows:
        #print(cs)
    # print(csv_rows)
    # print("\n\n\n************\n\n\n")

    debt_rows = select_all_db_debts(db)
    for debt_row in debt_rows:
        copy = profits_fixed(fix_multiple(db_to_panda(db, "users")))
        # print(copy)
        payer = debt_row[1]
        receiver = debt_row[2]
        amount = debt_row[3]
        # print(f"{payer} PAID {receiver} : {amount}")
        payer_profit = 0.0
        receiver_profit = 0.0
        try:
            for ps in copy.loc[copy["poker_username"] == payer]["profit"]:
                payer_profit = payer_profit + ps
            for rs in copy.loc[copy["poker_username"] == receiver]["profit"]:
                receiver_profit = receiver_profit + rs
        except:
            receiver_profit = copy.loc[copy["poker_username"] == receiver]["profit"].item()
            payer_profit = copy.loc[copy["poker_username"] == payer]["profit"].item()
        final_payer = payer_profit + amount
        final_receiver = receiver_profit - amount
        # copy.loc[copy["poker_username"] == payer, "profit"]["profit"] = final_payer
        # copy.loc[copy["poker_username"] == receiver, "profit"]["profit"] = final_receiver
        # print(f"{receiver_profit} : {receiver}")
        # print(f"{payer_profit} : {payer}")
        # print(f"\nFINAL : {final_receiver} : {receiver}")
        # print(f"FINAL : {final_payer} : {payer}")
        # print(f"amount : {amount}")
        # print("\n")
        # print(f"Payer profit {payer_profit} : {payer}")
        # print(f"Receiver profit {receiver_profit} : {receiver}")
        # print(f"Amount {amount}\n")
        update_db_users_global(db, (final_payer, payer))
        update_db_users_global(db, (final_receiver, receiver))
        # copy.loc[copy["poker_username"] == payer, "poker_username"]["profit"] = payer_profit + amount
        # copy.loc[copy["poker_username"] == receiver, "poker_username"]["profit"] = receiver_profit - amount
    # print(copy)
    # copy.to_sql('users', db, if_exists='replace', index=False)
    # print("DONE")
    delete_all_db_debts(db)



def final_calc(db):
    last_start = -1
    data = profits_fixed(fix_multiple(db_to_panda(db, "users")))
    m_list = data['profit'].tolist()
    # 0 -> player_id
    # 1 -> poker_username
    # 2 -> telegram_username
    # 3 -> telegram_chat_id
    # 4 -> payment_link
    # 5 -> profit
    final_data = {}
    m_list = sorted(m_list, reverse=False)
    # print(data)
    #  print(m_list)
    try:
        for num in m_list:
            # print("THE NUM: ", num)
            if num < 0:
                payer_row = data.iloc[m_list.index(num)]
                # print(payer_row)
                payer_name = payer_row["poker_username"]
                # print(f"The payer name is :{payer_name}")
                final_data[payer_name] = {}
                final_data[payer_name]["total"] = 0.0
                receivers_dict = {}
                # print(f"{payer_row['Player']} : ", num)
                temp = num
                while not temp == 0:
                    temp_old = temp
                    # print("temp : ", temp)
                    temp_abs = abs(temp)
                    amount = 0
                    receiver_row = data.iloc[last_start]
                    receiver_name = receiver_row["poker_username"]
                    receivers_dict[receiver_name] = {}
                    # print(f"The receiver name is :{receiver_name}")
                    if temp_abs == m_list[last_start]:
                        amount = temp_abs
                        temp = 0
                        m_list[last_start] = 0
                    elif temp_abs < m_list[last_start]:
                        amount = temp_abs
                        temp = 0
                        m_list[last_start] = m_list[last_start] - temp_abs
                    elif temp_abs > m_list[last_start]:
                        amount = m_list[last_start]
                        temp += m_list[last_start]
                        m_list[last_start] = 0
                    receivers_dict[receiver_name] = {
                        'amount': amount,
                        'payment_method': receiver_row["payment_link"]
                    }
                    if m_list[last_start] == 0:
                        last_start -= 1
                    # print("temp now : ", temp)
                    # print(m_list, "\n")
                    ind = m_list.index(temp_old)
                    m_list[ind] = temp
                    final_data[payer_name]["total"] = final_data[payer_name]["total"] + amount

                final_data[payer_name]['receivers'] = receivers_dict
                # print("After", m_list, "\n\n")
            else:
                continue
    except ValueError or KeyError:
        return {}
    # print("\n\nFINAL : \n\n", final_data)
    return final_data
