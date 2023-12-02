const TextToSVG = require('text-to-svg');
const textToSVG = TextToSVG.loadSync();

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', (line) => {
  try {
    // Parse the JSON line
    const data = JSON.parse(line);
    
    // Extract attributes, options, and text
    const { attributes, options, text } = data;
    
    // Update options with the textToSVG instance
    options.attributes = attributes;

    // Generate the SVG
    const svg = textToSVG.getSVG(text, options);

    // Output the SVG, removing newline characters
    console.log(svg.replace(/\n/g, ''));
  } catch (error) {
    console.error('Error processing line:', error.message);
  }
});
