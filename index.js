const express = require('express');
const bodyParser = require('body-parser');
const { PythonShell } = require('python-shell');
const path = require('path');
const app = express();
const port = 3000;

app.use(bodyParser.json()); // Parses incoming requests with JSON payloads.
app.use(bodyParser.urlencoded({ extended: true })); // Parses incoming requests with URL-encoded payloads.
// Custom middleware to set CORS headers, allowing all origins and specific headers in requests.
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
});

app.get('/scrape', (req, res) => {
    const options = {
        scriptPath: path.join(__dirname, 'scripts'), // Specifies the directory where the Python script is located.
        args: [],
        pythonOptions: ['-u'], // unbuffered output
        stdio: ['pipe', 'pipe', 'pipe'] // Configures the standard I/O streams
    };

    console.log("Starting Python script...");

    //Creates a new instance of PythonShell 
    let pyshell = new PythonShell('myntra_scraper.py', options);

    let outputMessages = []; // store messages from the Python script

    pyshell.on('message', (message) => {
        console.log("Python script message:", message);
        outputMessages.push(message);
    });

    pyshell.on('stderr', (stderr) => {
        console.error("Python script error:", stderr);
        outputMessages.push(`Error: ${stderr}`);
    });

    pyshell.end((err, code, signal) => {
        if (err) {
            console.error("Error running Python script:", err);
            res.status(500).send({ error: err.message, output: outputMessages });
        } else {
            console.log(`Python script finished with code ${code} and signal ${signal}`);
            res.status(200).send({ message: 'Scraping complete', output: outputMessages });
        }
    });
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
