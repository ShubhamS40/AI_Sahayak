const express = require("express");
const multer = require("multer");
const cors = require("cors");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const Together = require("together-ai");

const app = express();
const port = 8000;

// Enable CORS
app.use(cors());

// Configure Multer for file uploads
const upload = multer({ dest: "uploads/" });

// Replace 'your-api-key-here' with your actual Together API key
const API_KEY = 'dbd65ef3ea28743eb9f6ed0df90a98971c5a014ec4ddbd3fca2bf087de1a73e0'; // Your Together API key here

// Initialize Together AI with API Key
const together = new Together({ apiKey: API_KEY });

// Function to fetch disease info using Together AI's Llama model
async function getDiseaseInfo(disease) {
    try {
        const response = await together.chat.completions.create({
            messages: [
                {
                    role: "user",
                    content: `Mujhe ${disease} ke baare mein detail mein batayein. Symptoms, causes, treatment, aur precautions bhi bataayein. Medicines kya honi chahiye aur kis type ka food lena chahiye. Skin diagnosis ko Hinglish mein samjhaayein.`
                },
            ],
            model: "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        });

        return response.choices[0].message.content;
    } catch (error) {
        console.error("Error fetching disease info:", error);
        return "Disease ki additional information nahi mil paayi.";
    }
}

// API Endpoint for Prediction
app.post("/predict", upload.single("file"), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
    }

    const imagePath = path.join(__dirname, req.file.path);

    // Run Python script for prediction
    const pythonProcess = spawn("python", ["skin.py", imagePath]);

    let responseData = "";

    pythonProcess.stdout.on("data", (data) => {
        responseData += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
        console.error(`Error: ${data}`);
    });

    pythonProcess.on("close", async (code) => {
        fs.unlinkSync(imagePath); // Delete the file after processing

        if (code === 0) {
            let result = JSON.parse(responseData);

            if (result.predicted_disease) {
                // Get extra disease details using Together AI (Llama model)
                let diseaseInfo = await getDiseaseInfo(result.predicted_disease);
                result.disease_info = diseaseInfo;
            }

            res.json(result);
        } else {
            res.status(500).json({ error: "Failed to process image" });
        }
    });
});

// Start Server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
