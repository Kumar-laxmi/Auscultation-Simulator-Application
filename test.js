const fs = require('fs');
const wav = require('node-wav');

const audioPath = 'app/static/audio/heart/acute_myocardial_infarction/A/combined_audio.wav'; // Replace this with the path to your audio file

// Read the WAV file
const fileBuffer = fs.readFileSync(audioPath);
const result = wav.decode(fileBuffer);

// Extract audio array and duration
const audioArray = result.channelData[0]; // Assuming a mono channel
const durationInSeconds = result.duration;

console.log('Audio Array:', audioArray);
console.log('Duration (seconds):', durationInSeconds);