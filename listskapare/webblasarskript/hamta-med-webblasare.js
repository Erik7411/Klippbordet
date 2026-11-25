#!/usr/bin/env node
// Öppnar en sida i en webbläsare utan fönster (Playwright/Chromium), kör ladda-allt.js
// så att alla poster laddas, och sparar den färdiga sidan som HTML.
//
//   node hamta-med-webblasare.js URL ut.html [max-rundor]
//
// Används av listskapare.py --webblasare. Kräver Playwright: npm install playwright
// följt av npx playwright install chromium.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [url, ut, maxRundor] = process.argv.slice(2);
  if (!url || !ut) {
    console.error('Användning: node hamta-med-webblasare.js URL ut.html [max-rundor]');
    process.exit(2);
  }
  const webblasare = await chromium.launch();
  try {
    const sida = await webblasare.newPage({ locale: 'sv-SE' });
    const svar = await sida.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    if (svar && svar.status() >= 400) {
      throw new Error(`Sidan svarade ${svar.status()}. Om sidan spärrar automatiska hämtningar: ` +
        'använd bokmärket i din egen webbläsare i stället.');
    }
    await sida.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await sida.evaluate(n => { window.LISTSKAPARE_SPARA = false; if (n) window.LISTSKAPARE_MAX_RUNDOR = n; },
      Number(maxRundor) || 0);
    const kod = fs.readFileSync(path.join(__dirname, 'ladda-allt.js'), 'utf8');
    const resultat = await sida.evaluate(kod);
    fs.writeFileSync(ut, await sida.content());
    console.error(`  webbläsaren: ${resultat}, sparade ${ut}`);
  } catch (e) {
    console.error(String(e.message || e));
    process.exitCode = 1;
  } finally {
    await webblasare.close();
  }
})();
