from flask import Flask, request, jsonify
import os
from mutagen.easyid3 import EasyID3

app = Flask(__name__)

# 1. OUR MOCK DATABASE
database = [
    {"artist": "Asake", "title": "Lonely At The Top"},
    {"artist": "Burna Boy", "title": "Ye"},
    {"artist": "Davido", "title": "Unavailable (feat. Musa Keys)"},
    {"artist": "Wizkid", "title": "Essence (Acoustic Version) [Live at the O2]"},
    {"artist": "Wizkid", "title": "Essence"},
    {"artist": "Tiwa Savage", "title": "Water And Garri (Extended Club Mix)"},
    {"artist": "Rema", "title": "Calm Down (with Selena Gomez) - Official Remix"},
    {"artist": "Rema", "title": "Calm Down"},
    {"artist": "Rema", "title": "Calms Down"},
    {"artist": "Rema", "title": "palms Down"},
    {"artist": "Olamide", "title": "Rock (Live Performance Edition)"},
    {"artist": "Tems", "title": "Free Mind (Sped Up Version)"},
    {"artist": "Davido", "title": "Unavailableee "},

]

# Create a temporary folder to save the MP3 just long enough to read its tags
os.makedirs('temp_uploads', exist_ok=True)

@app.route('/api/musics', methods=['POST'])
def mock_upload():
    # Grab the title from the Postman form-data
    song_title = request.form.get('title')
    # Grab the MP3 file from the Postman form-data
    music_file = request.files.get('musicFile')

    # Failsafe if the user forgot to attach something
    if not song_title or not music_file:
        return jsonify({"error": "Missing title or musicFile!"}), 400

    # Save the file temporarily to read the hidden ID3 tags
    temp_path = os.path.join('temp_uploads', music_file.filename)
    music_file.save(temp_path)

    try:
        # Read the tags using Mutagen
        audio = EasyID3(temp_path)
        # Extract the artist name. If it has no tag, we call it "Unknown Artist"
        artist_name = audio.get('artist', ['Unknown Artist'])[0]
    except Exception:
        artist_name = "Unknown Artist"
    finally:
        # Clean up and delete the temp file immediately
        os.remove(temp_path)

    # ==========================================
    # 2. THE VALIDATION LOGIC (The Compound Check + Space Stripping)
    # ==========================================
    # We clean the incoming data first by removing accidental spaces at the start/end
    clean_incoming_artist = artist_name.strip().lower()
    clean_incoming_title = song_title.strip().lower()

    for track in database:
        # We also clean the database data just to be 100% safe
        clean_db_artist = track['artist'].strip().lower()
        clean_db_title = track['title'].strip().lower()

        # Now we compare the perfectly clean, space-free text
        if clean_db_artist == clean_incoming_artist and clean_db_title == clean_incoming_title:
            return jsonify({
                "status": "error",
                "message": f"409 Conflict: The song '{song_title.strip()}' by {artist_name.strip()} is already in the database!"
            }), 409
    
    # ==========================================
    # 3. SUCCESS PIPELINE (If no duplicate is found)
    # ==========================================
    # We save the cleaned-up version to the database so we don't store messy spaces
    database.append({"artist": artist_name.strip(), "title": song_title.strip()})
    
    return jsonify({
        "status": "success", 
        "message": f"Music queued for processing successfully",
        "saved_data": {"artist": artist_name.strip(), "title": song_title.strip()},
        "total_songs_in_db": len(database)
    }), 200


# ==========================================
# 4. THE GET ENDPOINT (To view the database)
# ==========================================
@app.route('/api/musics/uploaded-artists', methods=['GET'])
def get_uploaded_artists():
    # Extract just the unique artist names from our database
    unique_artists = list(set([track['artist'] for track in database]))
    
    return jsonify({
        "status": "success",
        "total_songs_in_db": len(database),
        "total_unique_artists": len(unique_artists),
        "artists": unique_artists,
        "full_database_list": database  # This shows you exactly what is inside!
    }), 200

if __name__ == '__main__':
    print("🚀 Mock JointEarn API running on http://127.0.0.1:5000")
    app.run(port=5000)
i am not a huiman x
