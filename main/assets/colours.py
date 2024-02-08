from flet import ThemeMode
import sqlite3
import os.path
import socket


class Colours:
    def __init__(self):
        db = sqlite3.connect(rf"assets\colourdeck.db")
        curs = db.cursor()
        #create the database if it doesn't exist
        #default is light mode
        exists = curs.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='Colours'").fetchone()
        if exists is None:
            curs.execute("CREATE TABLE IF NOT EXISTS Colours(ColoursID VARCHAR(8) primary key, ColourHex VARCHAR(32))")
            curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('BACKGROUND_COLOUR', '#FFFFFF')")
            curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('THEME_COLOUR', '#afe7ed')")
            curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('TEXT_COLOUR', '#424242')")
            curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('BACKGROUND_COLOUR_2', '#FAF9F6')")
            curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('thememode', 'LIGHT')")
            db.commit()
            
        #get the colours from the database
        self.BACKGROUND_COLOUR = curs.execute("SELECT ColourHex FROM Colours WHERE ColoursID='BACKGROUND_COLOUR'").fetchone()[0]
        self.THEME_COLOUR = curs.execute("SELECT ColourHex FROM Colours WHERE ColoursID='THEME_COLOUR'").fetchone()[0]
        self.TEXT_COLOUR = curs.execute("SELECT ColourHex FROM Colours WHERE ColoursID='TEXT_COLOUR'").fetchone()[0]
        self.BACKGROUND_COLOUR_2 = curs.execute("SELECT ColourHex FROM Colours WHERE ColoursID='BACKGROUND_COLOUR_2'").fetchone()[0]
        thememode = curs.execute("SELECT ColourHex FROM Colours WHERE ColoursID='thememode'").fetchone()[0]
        curs.close()
        db.close()
        
        #set the thememode
        if thememode == "LIGHT":
            self.thememode = ThemeMode.LIGHT
        elif thememode == "DARK":
            self.thememode = ThemeMode.DARK

    def get_colours(self): 
        return self.BACKGROUND_COLOUR, self.THEME_COLOUR, self.TEXT_COLOUR, self.BACKGROUND_COLOUR_2
    
    def get_bg(self):
        return self.themeColour1
    
    def get_nav_bar_colour(self):
        if self.get_theme() == ThemeMode.LIGHT:
            return "#FFF5EE"
        else:
            return "#40404F"

    def get_theme(self):
        return self.thememode
    
    def set_light_mode(self):
        db = sqlite3.connect(rf"assets\colourdeck.db")
        curs = db.cursor()
        curs.execute("CREATE TABLE IF NOT EXISTS Colours(ColoursID VARCHAR(8) primary key, ColourHex VARCHAR(32))")
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('BACKGROUND_COLOUR', '#FFFFFF')")
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('THEME_COLOUR', '#afe7ed')")
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('TEXT_COLOUR', '#424242')")
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('BACKGROUND_COLOUR_2', '#FAF9F6')")
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('thememode', 'LIGHT')")
        curs.close()
        db.commit()
        db.close()

        
    def set_dark_mode(self):
        db = sqlite3.connect(rf"assets\colourdeck.db")
        curs = db.cursor()
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('BACKGROUND_COLOUR', '#2C3A4A')")
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('THEME_COLOUR', '#E74C3C')")
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('TEXT_COLOUR', '#2C3E50')")
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('BACKGROUND_COLOUR_2', '#313C45')")
        curs.execute("INSERT OR REPLACE INTO Colours (ColoursID, ColourHex) VALUES ('thememode', 'DARK')")
        curs.close()
        db.commit()
        db.close()


