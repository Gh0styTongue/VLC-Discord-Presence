# VLC-Discord-Presence

**VLC-Discord-Presence** is a Python-based application that integrates VLC Media Player with Discord's rich presence feature. It shows your current VLC media status (whether you're playing, paused, or stopped), including the media's title, progress, and time left on the track. It also works in the background, even when the command prompt is minimized.

## Features

- Displays the current media title, progress, and time left.
- Shows whether the media is playing, paused, or stopped.
- Works in the background, without the need for the command prompt to remain open.
- Supports all types of audio and video extensions.
- Customizable VLC server connection settings (host, port, and password).
- Updated every 4.5 seconds with accurate media information.

## Requirements

- Python 3.x
- VLC Media Player (with the HTTP interface enabled)
- PyQt5 (for the setup window)
- `pypresence` library (for Discord integration)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/YourUsername/VLC-Discord-Presence.git
    ```

2. Navigate to the project folder:

    ```bash
    cd VLC-Discord-Presence
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up VLC Media Player:
   - Open VLC and go to `Tools > Preferences > Show settings: All`.
   - Under `Interface > Main interfaces`, check `HTTP`.
   - Set your desired password (this will be used for authentication).

## Usage

1. Run the script to launch the setup window, where you can input your VLC host, port, and password.
   
    ```bash
    python vlc_discord_presence.py
    ```

2. Once the setup is complete, the program will automatically start updating your Discord presence based on your VLC media status.

3. You can minimize the command prompt, and the program will continue running in the background.

## How It Works

- The application connects to the VLC server via HTTP.
- It checks the media status and extracts information such as the title, progress, and time left.
- It then updates the Discord status with this information, including whether the media is playing, paused, or stopped.
- The program runs in the background and updates the status every 4.5 seconds.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
