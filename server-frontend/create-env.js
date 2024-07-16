import fs from 'fs';
import path, { dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

let API_URL;
console.log('node_env', process.env.MY_CUSTOM_ENV)

if (process.env.MY_CUSTOM_ENV === 'development') {
    API_URL = "http://localhost:8002";
} else {
//    API_URL = "https://c964capstone-3cdvungrkq-uc.a.run.app:8000"
    API_URL = "http://localhost:8002";
}

const fileContents = `export const API_URL = \"${API_URL}\";`
const filePath = path.resolve(__dirname, 'src', 'build-constants.js');
fs.writeFileSync(filePath, fileContents);