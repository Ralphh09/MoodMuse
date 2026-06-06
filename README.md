# 🎶 MoodMuse

A mood-based music playlist generator powered by Spotify. Select your mood, take a quiz, or search for songs to get personalized playlists tailored to how you're feeling.

## Features

✨ **Mood-Based Playlists** - Generate playlists based on your current mood (Happy, Sad, Calm, Stressed, Angry)

🧠 **Mood Detection Quiz** - Take a 5-question quiz to have your mood detected automatically

❤️ **Favorite Songs** - Save your favorite tracks and access them anytime

📝 **Mood Journal** - Keep track of your moods and feelings over time

📋 **Mood History** - View your playlist generation history with charts

🔍 **Song Search** - Search for specific songs and artists on Spotify

🎨 **Custom Moods** - Create your own custom moods with custom emojis, colors, and genres

## Installation

### Prerequisites
- Python 3.8+
- Spotify Developer Account (for API credentials)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Ralphh09/MoodMuse.git
cd MoodMuse
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get Spotify API Credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app
   - Copy your Client ID and Client Secret

4. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

5. Edit `.env` and add your Spotify credentials:
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

6. Run the app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

### 🏠 Home Page
- Select a mood from the dropdown
- Choose how many songs you want (3-10)
- Click "Generate Playlist" to get recommendations
- Use "Shuffle Again" to get new recommendations

### 🧠 Mood Quiz
- Answer 5 quick questions about your energy, feelings, and preferences
- The app will detect your mood and generate a playlist

### 📋 History
- View all your past playlist generations
- See a chart of your mood distribution over time

### ❤️ Favorites
- All songs you've saved appear here
- Quick links to open songs on Spotify

### 📝 Journal
- Write down your thoughts and feelings
- Each entry is tagged with the mood you selected
- Keep a mood diary over time

### 🔍 Search
- Search for any song or artist
- Rate songs with stars
- Save songs to your favorites

### 🎨 Custom Moods
- Create your own moods beyond the default 5
- Set custom emojis, colors, and genres
- Use them to generate playlists

## Mood Themes

| Mood | Emoji | Genre | Color |
|------|-------|-------|-------|
| Happy | 😄 | Pop | Gold |
| Sad | 😢 | Acoustic | Blue |
| Calm | 😌 | Ambient | Green |
| Stressed | 😰 | Piano | Purple |
| Angry | 😤 | Classical | Red |

## Data Storage

MoodMuse stores all user data locally in JSON files:
- `mood_history.json` - Playlist generation history (last 50 entries)
- `favourites.json` - Saved favorite songs
- `mood_journal.json` - Journal entries (last 100)
- `song_ratings.json` - Star ratings for songs
- `custom_moods.json` - Custom mood definitions

## Environment Variables

The app uses environment variables to securely store Spotify credentials. Create a `.env` file with:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

**Never commit `.env` to version control.** The `.gitignore` file is configured to exclude it.

## Technologies Used

- **Streamlit** - Web app framework
- **Spotipy** - Spotify API wrapper
- **Pandas** - Data analysis and visualization
- **Python-dotenv** - Environment variable management
- **Python** - Core language

## File Structure

```
MoodMuse/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Future Enhancements

- 🎵 Spotify authentication for user playlists
- ☁️ Cloud storage for user data
- 🤖 Machine learning for better mood detection
- 🎯 Mood trends and analytics
- 🌐 Multi-language support
- 📱 Mobile app version

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

---

**Made with 🎵 by Ralphh09**
