const fs = require('fs');

const html = fs.readFileSync('public/index.html', 'utf8');
const scriptStart = html.indexOf('<script type="text/babel">');
const scriptEnd = html.lastIndexOf('</script>');
const js = html.substring(scriptStart + 26, scriptEnd);
console.log('Script length:', js.length);

// Check matching braces and parens
let braces = 0;
let parens = 0;
let brackets = 0;
for (let i = 0; i < js.length; i++) {
  if (js[i] === '{') braces++;
  if (js[i] === '}') braces--;
  if (js[i] === '(') parens++;
  if (js[i] === ')') parens--;
  if (js[i] === '[') brackets++;
  if (js[i] === ']') brackets--;
}
console.log('Balance: braces=' + braces + ', parens=' + parens + ', brackets=' + brackets);
