import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkcalendar import Calendar
from datetime import datetime
import cx_Oracle
#pip install cx_Oracle

cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_12")

def connect_to_db():
    try:
        connection = cx_Oracle.connect('bd072', 'bd072', 'bd-dc.cs.tuiasi.ro:1539/orcl')
        return connection
    except cx_Oracle.DatabaseError as e:
        print(f"Error: {e}")
        return None

def close_connection():
    global connection
    if connection:
        connection.close()
        print("Conexiunea la baza de date a fost închisă cu succes.")
    else:
        print("Nu există nicio conexiune la baza de date de închis.")

def open_players():
    def select_date():
        def print_sel():
            selected_date = cal.selection_get()
            formatted_date = selected_date.strftime("%m/%d/%Y")
            birth_date_entry.delete(0, 'end')
            birth_date_entry.insert(0, formatted_date)
            top.destroy()

        top = tk.Toplevel(new_window)
        today = datetime.now()
        cal = Calendar(top, selectmode='day',
                        month=today.month, day=today.day, year=today.year)
        cal.pack(padx=10, pady=10)
        confirm_button = tk.Button(top, text="Confirm", command=print_sel)
        confirm_button.pack(pady=10)

    new_window = tk.Toplevel(root)
    new_window.title("Tabela PLAYERS")

    tk.Label(new_window, text="Prenume").grid(row=0, column=0, padx=10, pady=10)
    first_name_entry = tk.Entry(new_window)
    first_name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Nume").grid(row=1, column=0, padx=10, pady=10)
    last_name_entry = tk.Entry(new_window)
    last_name_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(new_window, text="CNP").grid(row=2, column=0, padx=10, pady=10)
    cnp_entry = tk.Entry(new_window)
    cnp_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Data de nastere").grid(row=3, column=0, padx=10, pady=10)
    birth_date_entry = tk.Entry(new_window)
    birth_date_entry.grid(row=3, column=1, padx=10, pady=10)
    date_button = tk.Button(new_window, text="...", command=select_date)
    date_button.grid(row=3, column=2, padx=10, pady=10)

    tk.Label(new_window, text="Nickname").grid(row=4, column=0, padx=10, pady=10)
    nickname_entry = tk.Entry(new_window)
    nickname_entry.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Team").grid(row=5, column=0, padx=10, pady=10)
    team_list = tk.Entry(new_window)
    team_list.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Scor").grid(row=6, column=0, padx=10, pady=10)
    scor_entry = tk.Entry(new_window)
    scor_entry.grid(row=6, column=1, padx=10, pady=10)

    tk.Label(new_window, text="ID Player\nDoar pentru Update/Delete!").grid(row=7, column=0, padx=10, pady=10)
    id_player_entry = tk.Entry(new_window)
    id_player_entry.grid(row=7, column=1, padx=10, pady=10)

    def check_create_table():
        try:
            connection = connect_to_db()
            cursor = connection.cursor()

            cursor.execute("SELECT count(*) FROM user_tables WHERE table_name = 'PLAYERS'")
            result = cursor.fetchone()

            if result[0] == 0:
                create_table_query = """
                CREATE TABLE PLAYERS (
                    player_id  NUMBER(4) NOT NULL,
                    first_name VARCHAR2(15) NOT NULL,
                    last_name  VARCHAR2(15),
                    cnp        VARCHAR2(8),
                    birth_date DATE,
                    nickname   VARCHAR2(15) NOT NULL,
                    team_id    NUMBER(4) NOT NULL,
                    score_id   NUMBER(3) NOT NULL,
                    CONSTRAINT players_pk PRIMARY KEY (player_id, team_id),
                    CONSTRAINT players_cnp_un UNIQUE (cnp),
                    CONSTRAINT players_scores_fk FOREIGN KEY (score_id) REFERENCES scores(score_id),
                    CONSTRAINT players_teams_fk FOREIGN KEY (team_id) REFERENCES teams(team_id)
                )
                """
                cursor.execute(create_table_query)
                connection.commit()
                print("Table 'PLAYERS' created successfully.")
            else:
                print("Table 'PLAYERS' already exists.")

            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    check_create_table()

    def display_players():
        try:
            connection = connect_to_db()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM players ORDER BY PLAYER_ID')

            players = cursor.fetchall()

            cursor.close()
            connection.close()

            table_window = tk.Toplevel()
            table_window.title("Players Table")

            tree = ttk.Treeview(table_window)
            tree['columns'] = ('PLAYER_ID', 'PRENUME', 'NUME', 'CNP', 'BIRTH_DATE', 'NICKNAME', 'TEAM_ID', 'SCORE_ID')

            tree.heading('#0', text='Index')
            tree.column('#0', width=50)
            for col_name in tree['columns']:
                tree.heading(col_name, text=col_name)
                tree.column(col_name, width=100)
            for idx, player in enumerate(players, start=1):
                tree.insert('', 'end', text=f'{idx}', values=player)
            tree.pack(expand=tk.YES, fill=tk.BOTH)
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def insert():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                first_name = first_name_entry.get()
                last_name = last_name_entry.get()
                cnp = cnp_entry.get()
                birth_date = birth_date_entry.get()
                nickname = nickname_entry.get()
                team_id = int(team_list.get())
                score_id = int(scor_entry.get())

                cursor.execute("SELECT player_id_sequence.nextval FROM dual")
                next_id = cursor.fetchone()[0]

                sql = """
                    INSERT INTO PLAYERS (PLAYER_ID, FIRST_NAME, LAST_NAME, CNP, BIRTH_DATE, NICKNAME, TEAM_ID, SCORE_ID)
                    VALUES (:player_id, :first_name, :last_name, :cnp, TO_DATE(:birth_date, 'MM/DD/YYYY'), :nickname, :team_id, :score_id)
                """
                cursor.execute(sql, {
                    'player_id': next_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'cnp': cnp,
                    'birth_date': birth_date,
                    'nickname': nickname,
                    'team_id': team_id,
                    'score_id': score_id
                })
                connection.commit()
                cursor.close()
                connection.close()
                print("Player inserted successfully!")
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def delete():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()
                player_id = id_player_entry.get()
                cursor.execute("DELETE FROM PLAYERS WHERE PLAYER_ID = :player_id", {'player_id': player_id})
                connection.commit()
                cursor.close()
                connection.close()
                print("Player deleted successfully!")
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def update():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                player_id = int(id_player_entry.get())
                first_name = first_name_entry.get()
                last_name = last_name_entry.get()
                cnp = cnp_entry.get()
                birth_date = birth_date_entry.get()
                nickname = nickname_entry.get()
                team_id = int(team_list.get())
                score_id = int(scor_entry.get())

                sql = """
                    UPDATE PLAYERS
                    SET FIRST_NAME = :first_name,
                        LAST_NAME = :last_name,
                        CNP = :cnp,
                        BIRTH_DATE = TO_DATE(:birth_date, 'MM/DD/YYYY'),
                        NICKNAME = :nickname,
                        TEAM_ID = :team_id,
                        SCORE_ID = :score_id
                    WHERE PLAYER_ID = :player_id
                """
                cursor.execute(sql, {
                    'player_id': player_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'cnp': cnp,
                    'birth_date': birth_date,
                    'nickname': nickname,
                    'team_id': team_id,
                    'score_id': score_id
                })
                connection.commit()
                cursor.close()
                connection.close()
                print("Player updated successfully!")
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    new_window.columnconfigure(8, weight=1)
    new_window.rowconfigure(0,weight=1)

    display_button = tk.Button(new_window, text="Display Players", command=display_players)
    display_button.grid(row=8, column=0, columnspan=3, pady=10)

    insert_button = tk.Button(new_window, text="Insert", command=insert)
    insert_button.grid(row=9, column=0, padx=10, pady=10)

    delete_button = tk.Button(new_window, text="Delete", command=delete)
    delete_button.grid(row=9, column=1, padx=10, pady=10)

    update_button = tk.Button(new_window, text="Update", command=update)
    update_button.grid(row=9, column=2, padx=10, pady=10)

def open_instructiuni():
    root = tk.Tk()
    root.title("Instructiuni")
    text = (
        "Pentru tabela PLAYERS :\n    Functia INSERT:\n        #Campul LAST_NAME trebuie sa contina obligatoriu "
        "valoare!\n        #Campul CNP este UNIC pentru fiecare jucator!\n        #Campul BIRTH_DATE trebuie sa "
        "contina o valoare intre 01.01.2000 : 31.12.2004!\n        #Campul NICKNAME trebuie sa contina obligatoriu "
        "valoare!\n        #Pentru campul SCORE_ID acesta trebuie sa existe in tabela SCORES!\n        #Pentru campul "
        "TEAM_ID aceasta trebuie sa existe in tabela TEAMS!\n    Functia DELETE:\n        #Inainte de a sterge o "
        "inregistrare asigurati-va\n         ca ati sters scorul si echipa corespunzatoare jucatorului!\n    Functia "
        "UPDATE:\n        #Nu modifica PLAYER_ID!\n        #Asigurati-va ca exista SCORE_ID si TEAM_ID inainte de "
        "update!\n\n"
        "Pentru tabela SCORES :\n    Functia INSERT:\n        #Campul HOUR_IN_GAME contine obligatoriu o valoare "
        "intre 0-9999!\n        #Campul GENERAL_SCORE contine valori intre 0-999!\n        #Campurile KILLS,DEATHS,"
        "ASSISTS contin valori intre 0-99!\n    Functia DELETE:\n        #Nu exista restrictii\n    Functia UPDATE:\n"
        "        #Nu modifica SCORE_ID!\n\n"
        "Pentru tabela TEAMS :\n    Functia INSERT:\n        #TEAM_NAME contine obligatoriu o valoare!\n        "
        "#Campul RESULT_ID contine obligatoriu o valoare valida din tabela RESULTS!\n        #Campurile WINS,LOSES "
        "contin valori intre 0-99!\n    Functia DELETE:\n        #Inainte de a sterge o inregistrare asigurati-va ca "
        "ati sters si RESULT_ID\n corespunzator din tablela RESULTS!\n    Functia UPDATE:\n        #Nu modifica "
        "TEAM_ID!\n        #Asigurati-va ca exista RESULT_ID inainte de update!\n\n"
        "Pentru tabela RESULTS :\n    Functia INSERT:\n        #TOTAL_POINTS contine obligatoriu o valoare intre "
        "0-9999!\n        #Campurile FIRST_ROUND,SECOND_ROUND si THIRD_ROUND\n         contin valori intre 0-999!\n"
        "    Functia DELETE:\n        #Nu exista restrictii!\n    Functia UPDATE:\n        #Nu modifica RESULT_ID!\n"
        "        #Asigurati validitatea datelor!"
    )
    label = tk.Label(root, text=text, justify='left')
    label.pack(padx=10, pady=10)
    root.mainloop()

def open_scores():
    new_window = tk.Toplevel(root)
    new_window.title("Tabela SCORES")

    tk.Label(new_window, text="Kills").grid(row=0, column=0, padx=10, pady=10)
    kills_entry = tk.Entry(new_window)
    kills_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Deaths").grid(row=2, column=0, padx=10, pady=10)
    deaths_entry = tk.Entry(new_window)
    deaths_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Assists").grid(row=3, column=0, padx=10, pady=10)
    assists_entry = tk.Entry(new_window)
    assists_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Ore in joc").grid(row=5, column=0, padx=10, pady=10)
    ore_entry = tk.Entry(new_window)
    ore_entry.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Rank Type").grid(row=6, column=0, padx=10, pady=10)
    rank_options = ["Professional", "Semipro", "Amateur"]
    rank_type_var = tk.StringVar(new_window)
    rank_type_var.set(rank_options[0])  # Set default value
    rank_dropdown = tk.OptionMenu(new_window, rank_type_var, *rank_options)
    rank_dropdown.grid(row=6, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Score ID\nDoar pentru Update/Delete!").grid(row=7, column=0, padx=10, pady=10)
    id_score_entry = tk.Entry(new_window)
    id_score_entry.grid(row=7, column=1, padx=10, pady=10)

    def check_create_table_scores():
        try:
            connection = connect_to_db()
            cursor = connection.cursor()

            cursor.execute("SELECT count(*) FROM user_tables WHERE table_name = 'SCORES'")
            result = cursor.fetchone()

            if result[0] == 0:
                create_table_query = """
                    CREATE TABLE SCORES (
                        score_id      NUMBER(3) NOT NULL,
                        general_score NUMBER(3),
                        kills         NUMBER(2),
                        deaths        NUMBER(2),
                        assists       NUMBER(2),
                        rank_type     VARCHAR2(12),
                        hours_in_game NUMBER(3) NOT NULL,
                        CONSTRAINT scores_pk PRIMARY KEY (score_id)
                    )
                """
                cursor.execute(create_table_query)

                cursor.execute("CREATE SEQUENCE scores_score_id_seq START WITH 1 NOCACHE ORDER")

                cursor.execute("""
                    CREATE OR REPLACE TRIGGER scores_score_id_trg 
                        BEFORE INSERT ON scores 
                        FOR EACH ROW
                        WHEN (new.score_id IS NULL)
                        BEGIN
                            :new.score_id := scores_score_id_seq.nextval;
                        END;
                    """)

                connection.commit()
                print("Table 'SCORES' created successfully.")
            else:
                print("Table 'SCORES' already exists.")

            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    check_create_table_scores()

    def display_scores():
        try:
            connection = connect_to_db()
            cursor = connection.cursor()

            update_general_score_sql = """
                UPDATE SCORES
                SET GENERAL_SCORE = 3 * KILLS + 2 * ASSISTS - 1 * DEATHS
            """
            cursor.execute(update_general_score_sql)
            connection.commit()

            cursor.execute('SELECT * FROM scores ORDER BY SCORE_ID')
            scores = cursor.fetchall()
            cursor.close()
            connection.close()

            table_window = tk.Toplevel()
            table_window.title("Scores Table")
            tree = ttk.Treeview(table_window)
            tree['columns'] = ('SCORE_ID', 'GENERAL_SCORE', 'KILLS', 'DEATHS', 'ASSISTS', 'RANK_TYPE', 'HOURS_IN_GAME')

            tree.heading('#0', text='Index')
            tree.column('#0', width=50)
            for col_name in tree['columns']:
                tree.heading(col_name, text=col_name)
                tree.column(col_name, width=100)

            for idx, score in enumerate(scores, start=1):
                tree.insert('', 'end', text=f'{idx}', values=score)

            tree.pack(expand=tk.YES, fill=tk.BOTH)

        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def insert():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                kills = int(kills_entry.get())
                deaths = int(deaths_entry.get())
                assists = int(assists_entry.get())
                ore = int(ore_entry.get())
                rank = rank_type_var.get()

                cursor.execute("SELECT score_id_sequence.nextval FROM dual")
                next_id = cursor.fetchone()[0]

                sql = """
                    INSERT INTO SCORES (SCORE_ID, KILLS, DEATHS, ASSISTS, RANK_TYPE, HOURS_IN_GAME, GENERAL_SCORE)
                    VALUES (:score_id, :KILLS, :DEATHS, :ASSISTS, :RANK_TYPE, :HOURS_IN_GAME, 3*:KILLS + 2*:ASSISTS - 1*:DEATHS)
                """

                cursor.execute(sql, {
                    'score_id': next_id,
                    'KILLS': kills,
                    'DEATHS': deaths,
                    'ASSISTS': assists,
                    'RANK_TYPE': rank,
                    'HOURS_IN_GAME': ore,
                })
                connection.commit()
                cursor.close()
                connection.close()
                print("Score inserted successfully!")
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def delete():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()
                score_id = id_score_entry.get()
                cursor.execute("DELETE FROM SCORES WHERE SCORE_ID = :score_id", {'score_id': score_id})
                connection.commit()
                cursor.close()
                connection.close()
                print("Score deleted successfully!")
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def update():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                score_id = int(id_score_entry.get())
                new_kills = int(kills_entry.get())
                new_deaths = int(deaths_entry.get())
                new_assists = int(assists_entry.get())
                new_ore = int(ore_entry.get())
                new_rank = rank_type_var.get()

                sql = """
                    UPDATE SCORES
                    SET KILLS = :new_kills,
                        DEATHS = :new_deaths,
                        ASSISTS = :new_assists,
                        RANK_TYPE = :new_rank,
                        HOURS_IN_GAME = :new_ore,
                        GENERAL_SCORE = 3*:new_kills + 2*:new_assists - 1*:new_deaths
                    WHERE SCORE_ID = :score_id
                """

                cursor.execute(sql, {
                    'score_id': score_id,
                    'new_kills': new_kills,
                    'new_deaths': new_deaths,
                    'new_assists': new_assists,
                    'new_rank': new_rank,
                    'new_ore': new_ore
                })
                connection.commit()
                cursor.close()
                connection.close()
                print("Score updated successfully!")
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    new_window.columnconfigure(8, weight=1)
    new_window.rowconfigure(0,weight=1)

    display_button = tk.Button(new_window, text="Display Scores", command=display_scores)
    display_button.grid(row=8, column=0, columnspan=3, pady=10)
    insert_button = tk.Button(new_window, text="Insert", command=insert)
    insert_button.grid(row=9, column=0, padx=10, pady=10)

    delete_button = tk.Button(new_window, text="Delete", command=delete)
    delete_button.grid(row=9, column=1, padx=10, pady=10)

    update_button = tk.Button(new_window, text="Update", command=update)
    update_button.grid(row=9, column=2, padx=10, pady=10)

def open_teams():
    new_window = tk.Toplevel(root)
    new_window.title("Tabela TEAMS")

    tk.Label(new_window, text="Team Name").grid(row=0, column=0, padx=10, pady=10)
    teamname_entry = tk.Entry(new_window)
    teamname_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Wins").grid(row=1, column=0, padx=10, pady=10)
    wins_entry = tk.Entry(new_window)
    wins_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Loses").grid(row=2, column=0, padx=10, pady=10)
    loses_entry = tk.Entry(new_window)
    loses_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Results").grid(row=3, column=0, padx=10, pady=10)
    rank_options = ["Castigatori", "Invinsi", "Super"]
    rank_type_var = tk.StringVar(new_window)
    rank_type_var.set(rank_options[0])
    rank_dropdown = tk.OptionMenu(new_window, rank_type_var, *rank_options)
    rank_dropdown.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(new_window, text="Team ID\nDoar pentru Update/Delete!").grid(row=4, column=0, padx=10, pady=10)
    id_teams_entry = tk.Entry(new_window)
    id_teams_entry.grid(row=4, column=1, padx=10, pady=10)

    def check_create_table_teams():
        try:
            connection = connect_to_db()
            cursor = connection.cursor()

            cursor.execute("SELECT count(*) FROM user_tables WHERE table_name = 'TEAMS'")
            result = cursor.fetchone()

            if result[0] == 0:
                create_table_query = """
                CREATE TABLE teams (
                    team_id   NUMBER(4) NOT NULL,
                    team_name VARCHAR2(15) NOT NULL,
                    wins      NUMBER(2),
                    loses     NUMBER(2),
                    result_id VARCHAR2(12) NOT NULL
                )
                """
                cursor.execute(create_table_query)

                cursor.execute("CREATE UNIQUE INDEX teams_result_id_idx ON teams(result_id)")

                cursor.execute("ALTER TABLE teams ADD CONSTRAINT teams_pk PRIMARY KEY (team_id)")

                cursor.execute("""
                ALTER TABLE teams
                    ADD CONSTRAINT teams_results_fk FOREIGN KEY (result_id)
                        REFERENCES results(result_id)
                """)

                cursor.execute("CREATE SEQUENCE teams_team_id_seq START WITH 1 NOCACHE ORDER")

                cursor.execute("""
                CREATE OR REPLACE TRIGGER teams_team_id_trg 
                    BEFORE INSERT ON teams 
                    FOR EACH ROW
                    WHEN (new.team_id IS NULL)
                    BEGIN
                        :new.team_id := teams_team_id_seq.nextval;
                    END;
                """)

                connection.commit()
                print("Table 'TEAMS' created successfully.")
            else:
                print("Table 'TEAMS' already exists.")

            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    check_create_table_teams()

    def display_teams():
        try:
            connection = connect_to_db()

            cursor = connection.cursor()

            cursor.execute('SELECT * FROM teams ORDER BY TEAM_ID')

            teams = cursor.fetchall()

            cursor.close()
            connection.close()

            table_window = tk.Toplevel()
            table_window.title("Teams Table")

            tree = ttk.Treeview(table_window)
            tree['columns'] = ('TEAM_ID', 'TEAM_NAME', 'WINS', 'LOSES', 'RESULT_ID')

            tree.heading('#0', text='Index')
            tree.column('#0', width=50)
            for col_name in tree['columns']:
                tree.heading(col_name, text=col_name)
                tree.column(col_name, width=100)

            for idx, teams in enumerate(teams, start=1):
                tree.insert('', 'end', text=f'{idx}', values=teams)

            tree.pack(expand=tk.YES, fill=tk.BOTH)

        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def insert():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                teamname = teamname_entry.get()
                wins = wins_entry.get()
                loses = loses_entry.get()
                rank = rank_type_var.get()

                cursor.execute("SELECT teams_id_sequence.nextval FROM dual")
                next_id = cursor.fetchone()[0]

                sql = """
                    INSERT INTO TEAMS(TEAM_ID, TEAM_NAME, WINS, LOSES, RESULT_ID)
                    VALUES (:TEAM_ID, :TEAM_NAME, :WINS, :LOSES, :RESULT_ID)
                """

                cursor.execute(sql, {
                    'team_id': next_id,
                    'TEAM_NAME': teamname,
                    'WINS': wins,
                    'LOSES': loses,
                    'RESULT_ID': rank,
                })
                connection.commit()
                cursor.close()
                connection.close()
                print("Score inserted successfully!")

        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def delete():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                team_id = id_teams_entry.get()

                cursor.execute("DELETE FROM TEAMS WHERE TEAM_ID = :team_id", {'team_id': team_id})
                connection.commit()
                cursor.close()
                connection.close()
                print("Team deleted successfully!")
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def update():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                team_id = int(id_teams_entry.get())
                new_teamname = teamname_entry.get()
                new_wins = int(wins_entry.get())
                new_loses = int(loses_entry.get())
                new_rank = rank_type_var.get()

                sql = """
                    UPDATE TEAMS
                    SET TEAM_NAME = :new_teamname,
                        WINS = :new_wins,
                        LOSES = :new_loses,
                        RESULT_ID = :new_rank
                    WHERE TEAM_ID = :team_id
                """

                cursor.execute(sql, {
                    'new_teamname': new_teamname,
                    'new_wins': new_wins,
                    'new_loses': new_loses,
                    'new_rank': new_rank,
                    'team_id': team_id,
                })
                connection.commit()
                cursor.close()
                connection.close()
                print("Team updated successfully!")
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    new_window.columnconfigure(8, weight=1)
    new_window.rowconfigure(0,weight=1)

    display_button = tk.Button(new_window, text="Display Teams", command=display_teams)
    display_button.grid(row=8, column=0, columnspan=3, pady=10)

    insert_button = tk.Button(new_window, text="Insert", command=insert)
    insert_button.grid(row=9, column=0, padx=10, pady=10)

    delete_button = tk.Button(new_window, text="Delete", command=delete)
    delete_button.grid(row=9, column=1, padx=10, pady=10)

    update_button = tk.Button(new_window, text="Update", command=update)
    update_button.grid(row=9, column=2, padx=10, pady=10)

def open_results():
    new_window = tk.Toplevel(root)
    new_window.title("Tabela RESULTS")

    def update_total_points(*args):
        try:
            first_round = int(first_type_var.get())
            second_round = int(second_type_var.get())
            third_round = int(third_type_var.get())

            total_points = first_round + second_round + third_round

            totalpoints_entry.config(state='normal')
            totalpoints_entry.delete(0, tk.END)
            totalpoints_entry.insert(0, str(total_points))
            totalpoints_entry.config(state='readonly')
        except ValueError:
            pass

    tk.Label(new_window, text="First Round").grid(row=0, column=0, padx=10, pady=10)
    first_options = ["0", "50", "100", "200"]
    first_type_var = tk.StringVar(new_window)
    first_type_var.set(first_options[0])  # Set default value
    first_dropdown = tk.OptionMenu(new_window, first_type_var, *first_options)
    first_dropdown.grid(row=0, column=1, padx=10, pady=10)
    first_type_var.trace('w', update_total_points)

    tk.Label(new_window, text="Second Round").grid(row=1, column=0, padx=10, pady=10)
    second_options = ["0", "50", "100", "200"]
    second_type_var = tk.StringVar(new_window)
    second_type_var.set(second_options[0])  # Set default value
    second_dropdown = tk.OptionMenu(new_window, second_type_var, *second_options)
    second_dropdown.grid(row=1, column=1, padx=10, pady=10)
    second_type_var.trace('w', update_total_points)

    tk.Label(new_window, text="Third Round").grid(row=2, column=0, padx=10, pady=10)
    third_options = ["0", "50", "100", "200"]
    third_type_var = tk.StringVar(new_window)
    third_type_var.set(third_options[0])  # Set default value
    third_dropdown = tk.OptionMenu(new_window, third_type_var, *third_options)
    third_dropdown.grid(row=2, column=1, padx=10, pady=10)
    third_type_var.trace('w', update_total_points)

    tk.Label(new_window, text="Total Points").grid(row=3, column=0, padx=10, pady=10)
    totalpoints_entry = tk.Entry(new_window)
    totalpoints_entry.grid(row=3, column=1, padx=10, pady=10)
    totalpoints_entry.config(state='readonly')

    update_total_points()

    tk.Label(new_window, text="Result ID\nDoar pentru Update/Delete!").grid(row=4, column=0, padx=10, pady=10)
    id_entry = tk.Entry(new_window)
    id_entry.grid(row=4, column=1, padx=10, pady=10)

    def check_create_table_results():
        try:
            connection = connect_to_db()
            cursor = connection.cursor()

            cursor.execute("SELECT count(*) FROM user_tables WHERE table_name = 'RESULTS'")
            result = cursor.fetchone()

            if result[0] == 0:
                create_table_query = """
                CREATE TABLE results (
                    result_id    NUMBER(4) NOT NULL,
                    first_round  NUMBER(3),
                    second_round NUMBER(3),
                    third_round  NUMBER(3),
                    total_points NUMBER(4) NOT NULL
                )
                """
                cursor.execute(create_table_query)

                cursor.execute("ALTER TABLE results ADD CONSTRAINT results_pk PRIMARY KEY (result_id)")

                cursor.execute("CREATE SEQUENCE results_result_id_seq START WITH 1 NOCACHE ORDER")

                cursor.execute("""
                CREATE OR REPLACE TRIGGER results_result_id_trg 
                    BEFORE INSERT ON results 
                    FOR EACH ROW
                    WHEN (new.result_id IS NULL)
                    BEGIN
                        :new.result_id := results_result_id_seq.nextval;
                    END;
                """)

                connection.commit()
                print("Table 'RESULTS' created successfully.")
            else:
                print("Table 'RESULTS' already exists.")

            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    check_create_table_results()

    def display_results():
        try:
            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM results ORDER BY RESULT_ID')
            teams = cursor.fetchall()
            cursor.close()
            connection.close()
            table_window = tk.Toplevel()
            table_window.title("Results Table")
            tree = ttk.Treeview(table_window)
            tree['columns'] = (
                'RESULT_ID', 'FIRST_ROUND', 'SECOND_ROUND', 'THIRD_ROUND', 'TOTAL_POINTS')

            tree.heading('#0', text='Index')
            tree.column('#0', width=50)
            for col_name in tree['columns']:
                tree.heading(col_name, text=col_name)
                tree.column(col_name, width=100)

            for idx, teams in enumerate(teams, start=1):
                tree.insert('', 'end', text=f'{idx}', values=teams)

            tree.pack(expand=tk.YES, fill=tk.BOTH)

        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def insert():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                first_round_value = int(first_type_var.get())
                second_round_value = int(second_type_var.get())
                third_round_value = int(third_type_var.get())
                total_points_value = int(totalpoints_entry.get())

                cursor.execute("SELECT result_id_sequence.nextval FROM dual")
                next_id = cursor.fetchone()[0]

                insert_query = """
                    INSERT INTO RESULTS (result_id, first_round, second_round, third_round, total_points)
                    VALUES (:result_id, :first_round, :second_round, :third_round, :total_points)
                """

                cursor.execute(insert_query, {
                    'result_id': next_id,
                    'first_round': first_round_value,
                    'second_round': second_round_value,
                    'third_round': third_round_value,
                    'total_points': total_points_value,
                })

                connection.commit()
                cursor.close()
                connection.close()
                print("Data inserted successfully!")

        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def delete():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                result_id = int(id_entry.get())

                delete_query = "DELETE FROM RESULTS WHERE result_id = :result_id"

                cursor.execute(delete_query, {'result_id': result_id})

                connection.commit()
                cursor.close()
                connection.close()
                print("Data deleted successfully!")

        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    def update():
        try:
            connection = connect_to_db()
            if connection:
                cursor = connection.cursor()

                result_id = int(id_entry.get())
                first_round_value = int(first_type_var.get())
                second_round_value = int(second_type_var.get())
                third_round_value = int(third_type_var.get())
                total_points_value = int(totalpoints_entry.get())

                update_query = """
                    UPDATE RESULTS
                    SET first_round = :first_round,
                        second_round = :second_round,
                        third_round = :third_round,
                        total_points = :total_points
                    WHERE result_id = :result_id
                """

                cursor.execute(update_query, {
                    'first_round': first_round_value,
                    'second_round': second_round_value,
                    'third_round': third_round_value,
                    'total_points': total_points_value,
                    'result_id': result_id,
                })

                connection.commit()
                cursor.close()
                connection.close()
                print("Data updated successfully!")

        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")

    new_window.columnconfigure(8, weight=1)
    new_window.rowconfigure(0,weight=1)

    display_button = tk.Button(new_window, text="Display Results", command=display_results)
    display_button.grid(row=8, column=0, columnspan=3, pady=10)

    insert_button = tk.Button(new_window, text="Insert", command=insert)
    insert_button.grid(row=9, column=0, padx=10, pady=10)

    delete_button = tk.Button(new_window, text="Delete", command=delete)
    delete_button.grid(row=9, column=1, padx=10, pady=10)

    update_button = tk.Button(new_window, text="Update", command=update)
    update_button.grid(row=9, column=2, padx=10, pady=10)

root = tk.Tk()
root.title("Lan Party Championship")

image_path = "Pro-Esports (1).jpg"
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

image_label = tk.Label(root, image=photo)
image_label.pack(side="left")

button_frame = tk.Frame(root)
button_frame.pack(side="right", padx=40, pady=20)

try:
    connection = cx_Oracle.connect('bd072', 'bd072', 'bd-dc.cs.tuiasi.ro:1539/orcl')
    print("Conexiunea la baza de date s-a realizat cu succes.")
except cx_Oracle.DatabaseError as e:
    print(f"Eroare la conexiunea la baza de date: {e}")

root.protocol("WM_DELETE_WINDOW", close_connection)

def button0_clicked():
    open_instructiuni()

def button1_clicked():
    open_players()

def button2_clicked():
    open_scores()

def button3_clicked():
    open_teams()

def button4_clicked():
    open_results()

def button5_clicked():
    exit(0)

button0 = tk.Button(button_frame, text="Instructiuni completare", command=button0_clicked)
button0.pack(pady=10)

button1 = tk.Button(button_frame, text="Tabela PLAYERS", command=button1_clicked)
button1.pack(pady=10)

button2 = tk.Button(button_frame, text="Tabela SCORES", command=button2_clicked)
button2.pack(pady=10)

button3 = tk.Button(button_frame, text="Tabela TEAMS", command=button3_clicked)
button3.pack(pady=10)

button4 = tk.Button(button_frame, text="Tabela RESULTS", command=button4_clicked)
button4.pack(pady=10)

button5 = tk.Button(button_frame, text="Inchidere program", command=button5_clicked)
button5.pack(pady=10)

root.mainloop()