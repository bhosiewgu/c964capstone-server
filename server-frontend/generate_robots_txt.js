// change this to check in
import fs from 'fs';
import path, { dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const robotsTxtContent = `User-agent: *
Disallow: /`;

const pathToWWW = path.resolve(__dirname, '..', 'www');

fs.writeFileSync(`${pathToWWW}/robots.txt`, robotsTxtContent);
