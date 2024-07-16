// change this to check in
const fs = require('fs')
const path = require('path')

const robotsTxtContent = `User-agent: *
Disallow: /`

const pathToWWW = path.resolve(__dirname, '..', 'www')

fs.writeFleSync(`${pathToWWW}/robots.txt`, robotsTxtContent)
