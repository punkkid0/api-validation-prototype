# JointEarn Media Validation API (Prototype)

A backend API validation prototype built to prevent duplicate media uploads and ensure data integrity for the JointEarn platform.

##  The Problem
Currently, our content pipeline involves team members uploading music and videos to the live app via Postman `POST` requests. Because the API intelligently extracts the **Artist Name** directly from the MP3 file's ID3 metadata tags (using only the `title` and `musicFile` in `form-data`), new team members are working blind. They have no way to know if a specific track has already been uploaded, creating a high risk of duplicate content flooding the database.

##  The Solution: The Compound Check
This repository contains a lightweight Python/Flask prototype that demonstrates a **Compound Validation Check**. 

To safely scale our data-entry team, the backend API must protect the database by doing the following during a `POST` request:
1. Extract the `Artist Name` from the ID3 tags.
2. Strip spaces and convert both the Artist Name and the incoming `Title` to lowercase.
3. Query the database to see if that exact **Artist + Title** combination already exists.
4. If it exists: Return a `409 Conflict` error (Reject).
5. If it is new: Process and return a `200 OK` (Accept).

---

##  Running the Prototype Locally

If you want to test the validation logic on your local machine:

**1. Install the requirements:**
```bash
pip install flask mutagen
```

**2. Run the server:**

Bash
python mock_api.py
The server will start on http://127.0.0.1:5000

 API Documentation (Mock Endpoints)
1. Upload Music (Validation Test)
    Endpoint: POST /api/musics
    
    Body (form-data):
    
    title: (Text) e.g., "Lonely At The Top"
    
    musicFile: (File) MP3 file properly tagged with ID3 metadata.
    
    Behavior: Checks the mock database for duplicates. Rejects exact matches (case-insensitive and space-trimmed) with a 409 Conflict.

2. View Uploaded Artists (Visibility Tool)
    Endpoint: GET /api/musics/uploaded-artists
    
    Behavior: Returns a distinct JSON list of all unique artist names currently in the database. This acts as a "Source of Truth" dashboard for the data-entry team.
    
     Implementation Guide for Backend Developers
    When moving this logic to the main JointEarn codebase, the validation check should look like this depending on the stack:
    
    For Node.js (Mongoose):

    ```bash
    const duplicateExists = await Track.exists({ 
    artist: extractedArtistName.trim().toLowerCase(), 
    title: providedSongTitle.trim().toLowerCase() 
    });
    if (duplicateExists) return res.status(409).json({ error: "Duplicate found" });
    ```

    For PHP (Laravel):
    ```bash
    $duplicateExists = Track::whereRaw('LOWER(artist_name) = ?', [strtolower(trim($extractedArtist))])
                        ->whereRaw('LOWER(title) = ?', [strtolower(trim($providedTitle))])
                        ->exists();
    if ($duplicateExists) return response()->json(['error' => 'Duplicate found'], 409);
    ```
    
