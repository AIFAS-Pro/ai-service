const fs = require("fs");
const path = require("path");

const aiServiceUrl = process.env.AI_SERVICE_URL;

if (!aiServiceUrl) {
    throw new Error("AI_SERVICE_URL environment variable is not set");
}

const config = `window.APP_CONFIG = {
    AI_SERVICE_URL: "${aiServiceUrl}"
};
`;

const configPath = path.join(__dirname, "js", "config.js");

fs.writeFileSync(configPath, config);

console.log("Generated js/config.js");
console.log("AI_SERVICE_URL:", aiServiceUrl);