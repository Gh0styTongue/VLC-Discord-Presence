import time
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
from pypresence import Presence
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import QSettings, QTimer
import sys
import webbrowser

client_id = "1347834940380676156"
vlc_host = "localhost"
vlc_port = 8080
vlc_username = ""
vlc_password = ""
discord_available = False

audio_extensions = [
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff', '.alac', '.amr', '.ape', '.opus',
    '.pcm', '.dsd', '.vaw', '.tta', '.wv', '.sda', '.mka', '.dts', '.ac3', '.aif', '.au', '.mid', '.midi',
    '.ra', '.ram', '.3ga', '.tta', '.mpc', '.spx', '.cda', '.caf', '.nsa', '.nsf', '.mod', '.s3m', '.it', '.xm', '.mtm'
]

video_extensions = [
    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.3gp', '.ogv', '.ts', '.m2ts',
    '.iso', '.vob', '.rm', '.rmvb', '.asf', '.m4v', '.f4v', '.swf', '.divx', '.h264', '.hevc', '.xvid', '.mpeg4',
    '.webm', '.mp2', '.mpv', '.mod', '.tod', '.mts', '.mj2', '.mpg2', '.avi', '.vfw', '.mov', '.dat', '.bik',
    '.m2v', '.vro', '.mpv', '.m2t', '.dv', '.dvr-ms', '.mkv', '.wmv', '.mov', '.mpegts', '.divx', '.x264', '.xvid'
]

try:
    from pypresence import Presence
    discord_available = True
except ImportError:
    discord_available = False

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def get_vlc_status():
    try:
        url = f"http://{vlc_host}:{vlc_port}/requests/status.xml"
        response = requests.get(url, auth=HTTPBasicAuth(vlc_username, vlc_password), timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            state = root.find("state").text
            if state == "playing":
                info = root.find(".//information/category[@name='meta']")
                if info is not None:
                    filename_elem = info.find(".//info[@name='filename']")
                    album_elem = info.find(".//info[@name='album']")
                    filename = filename_elem.text if filename_elem is not None else "Unknown File"
                    album = album_elem.text if album_elem is not None else None
                    filename_no_ext = os.path.splitext(filename)[0] if filename else "Unknown File"
                    position_elem = root.find(".//time")
                    length_elem = root.find(".//length")
                    position = float(position_elem.text) if position_elem is not None else 0
                    length = float(length_elem.text) if length_elem is not None else 0

                    time_left = length - position
                    time_played = position

                    is_audio = any(filename.lower().endswith(ext) for ext in audio_extensions)
                    is_video = any(filename.lower().endswith(ext) for ext in video_extensions)

                    return {
                        "state": "playing",
                        "filename": filename_no_ext,
                        "album": album,
                        "is_audio": is_audio,
                        "is_video": is_video,
                        "time_played": time_played,
                        "time_left": time_left
                    }
            return {"state": state}
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error in get_vlc_status: {e}")
        return None

def start_presence():
    global client_id, discord_available
    RPC = None
    print_counter = 0
    if discord_available and client_id:
        try:
            RPC = Presence(client_id)
            RPC.connect()
        except Exception as e:
            print(f"Error while connecting to Discord: {e}")
            discord_available = False

    while True:
        try:
            vlc_status = get_vlc_status()
            if vlc_status:
                if vlc_status["state"] == "playing":
                    action = "Listening" if vlc_status["is_audio"] else "Watching"
                    status_text = f"{action}: {vlc_status['filename']} - {format_time(vlc_status['time_played'])} / {format_time(vlc_status['time_left'])}"

                    status_text = status_text.replace('_', ' ')

                    large_image = vlc_status["album"].lower().replace(" ", "_") if vlc_status["album"] else "vlc"
                    if discord_available and RPC:
                        try:
                            RPC.update(
                                state="VLC Media Player",
                                details=status_text,
                                large_image=large_image,
                                large_text=vlc_status["album"] if vlc_status["album"] else "VLC Media Player"
                            )
                            print(f"Updated Discord presence: {status_text}")
                            print_counter += 1
                            if print_counter >= 3:
                                print("\033c", end="")
                                print_counter = 0
                        except Exception as e:
                            print(f"Error while updating Discord status: {e}")
                            pass
                elif vlc_status["state"] in ["paused", "stopped"]:
                    if vlc_status.get("filename"):
                        status_text = f"Watching: {vlc_status['filename']} - {format_time(vlc_status['time_played'])} / {format_time(vlc_status['time_left'])} [PAUSED]"
                    else:
                        status_text = "Media Paused"

                    if discord_available and RPC:
                        try:
                            RPC.update(
                                state="VLC Media Player",
                                details=status_text,
                                large_image="vlc",
                                large_text="VLC Media Player"
                            )
                            print(f"Updated Discord presence: {status_text}")
                        except Exception as e:
                            print(f"Error while updating Discord status for paused media: {e}")
                            pass
            else:
                if discord_available and RPC:
                    RPC.clear()
            time.sleep(4.5)
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(4.5)

class SetupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VLC Discord Presence Setup")
        self.setGeometry(300, 300, 300, 200)
        layout = QVBoxLayout()
        self.password_label = QLabel("VLC Password:")
        layout.addWidget(self.password_label)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.save_and_start)
        button_layout.addWidget(self.start_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        settings = QSettings("vlc_discord_presence.ini", QSettings.IniFormat)
        global vlc_password
        vlc_password = settings.value("vlc_password", "")
        self.password_input.setText(vlc_password)

    def save_and_start(self):
        global vlc_password
        try:
            settings = QSettings("vlc_discord_presence.ini", QSettings.IniFormat)
            settings.setValue("vlc_password", self.password_input.text())
            vlc_password = self.password_input.text()
            QMessageBox.information(self, "Success", "Settings saved successfully.")
            self.close()
            start_presence()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            print(f"Error while saving settings: {e}")

def check_authorization():
    auth_url = "https://discord.com/oauth2/authorize?client_id=1347834940380676156&response_type=code&redirect_uri=https%3A%2F%2Fvideolan.org%2Fvlc%2F&scope=presences.write"
    webbrowser.open(auth_url)
    time.sleep(5)
    QMessageBox.information(None, "Authorization", "Authorization check completed.")
    settings = QSettings("vlc_discord_presence.ini", QSettings.IniFormat)
    settings.setValue("discord_authorized", "true")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = SetupWindow()
        window.show()
        app.exec_()
    except Exception as e:
        print(f"Error in main execution: {e}")
        QMessageBox.critical(None, "Critical Error", f"A critical error occurred: {e}")
