// Listskapare: ladda allt. Fungerar på sidor som visar en lista lite i taget, med en
// knapp av typen "Visa fler" eller "Load more", eller som laddar mer när man scrollar.
// Skriptet klickar eller scrollar tills inget mer laddas, och sparar sedan hela sidan som
// HTML. Den filen läser listskapare.py ("python3 listskapare.py sidan.html --visa").
//
// På IMDb-listor sparas i stället titlarna direkt som .txt, en per rad.
//
// Körs som bokmärke (se README.md), i konsolen (F12 > Console), eller av
// hamta-med-webblasare.js, som då sätter window.LISTSKAPARE_SPARA = false.
(async () => {
  const MAX_RUNDOR = window.LISTSKAPARE_MAX_RUNDOR || 300;
  const PAUS = 1200;                 // ms mellan rundorna, för att inte belasta sidan
  const VANTA_KNAPP = 10000;         // ms att vänta på nytt innehåll efter ett klick
  const VANTA_SCROLL = 4000;         // ms att vänta efter en scrollning
  const SPARA = window.LISTSKAPARE_SPARA !== false;
  const sov = ms => new Promise(r => setTimeout(r, ms));

  const KNAPPTEXT = /^\s*(\d+\s+)?(visa|ladda|hämta|läs in|se|load|show|see|view|get)?\s*(fler|mer|more)(\s+\S+){0,2}\s*$/i;
  const INTE = /\b(läs mer|read more|mer info|more info|mer om|learn more)\b/i;
  const syns = el => el.offsetParent !== null && !el.disabled && el.getAttribute('aria-disabled') !== 'true';
  const provade = new WeakSet();  // knappar som inte gav något nytt (t.ex. menyknappar)
  const knapp = () => [...document.querySelectorAll('button, [role=button], a, input[type=button]')]
    .filter(el => {
      if (provade.has(el)) return false;
      const t = (el.value || el.textContent || '').trim();
      if (!t || t.length > 40 || !KNAPPTEXT.test(t) || INTE.test(t) || !syns(el)) return false;
      if (el.tagName === 'A') {   // länkar som byter sida hoppas över: då tappas det laddade
        const h = el.getAttribute('href') || '';
        return !h || h === '#' || h.startsWith('javascript:');
      }
      return true;
    })
    .pop();  // den sista: "visa fler" ligger oftast under listan
  const matt = () => document.body.getElementsByTagName('*').length;

  let ruta = null;
  if (SPARA) {
    ruta = document.createElement('div');
    ruta.style.cssText = 'position:fixed;top:12px;right:12px;z-index:2147483647;background:#06202b;' +
      'color:#f2fbfa;font:15px/1.4 sans-serif;padding:12px 16px;border-radius:8px;' +
      'box-shadow:0 4px 16px rgba(0,0,0,.4);max-width:320px';
    document.body.appendChild(ruta);
  }
  const visa = t => { if (ruta) ruta.textContent = 'Listskapare: ' + t; else console.log(t); };

  let missar = 0, klick = 0, scroll = 0;
  for (let runda = 1; runda <= MAX_RUNDOR && missar < 2; runda++) {
    const fore = matt();
    const b = knapp();
    if (b) { b.scrollIntoView({ block: 'center' }); b.click(); klick++; }
    else { window.scrollTo(0, document.documentElement.scrollHeight); scroll++; }
    visa(`runda ${runda}: ${b ? 'klickade "' + b.textContent.trim() + '"' : 'scrollade'} …`);
    const start = Date.now();
    while (matt() <= fore && Date.now() - start < (b ? VANTA_KNAPP : VANTA_SCROLL)) await sov(250);
    if (matt() > fore) missar = 0;
    else if (b) provade.add(b);   // prova scroll eller annan knapp nästa runda
    else missar++;
    await sov(PAUS);
  }
  const resultat = `${klick} klick, ${scroll} scrollningar`;

  if (!SPARA) return resultat;
  const namn = (document.title || 'sida').replace(/[^\wåäöÅÄÖ-]+/g, '-').replace(/^-+|-+$/g, '').toLowerCase() || 'sida';
  const ladda = (innehall, typ, fil) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([innehall], { type: typ + ';charset=utf-8' }));
    a.download = fil;
    document.body.appendChild(a); a.click(); a.remove();
  };

  // IMDb-listor sparas direkt som .txt, "Titel (år)", en per rad
  const imdb = /(^|\.)imdb\.com$/.test(location.hostname)
    ? [...document.querySelectorAll('li.ipc-metadata-list-summary-item')] : [];
  if (imdb.length) {
    const rensa = t => (t || '').replace(/\s+/g, ' ').replace(/^\s*\d+\.\s*/, '').trim();
    const rader = imdb.map(li => {
      // Rubriken i första hand, annars länken till filmens sida (/title/tt…)
      let titel = rensa(li.querySelector('h3, .ipc-title__text')?.textContent);
      if (!titel) {
        const lank = [...li.querySelectorAll('a[href*="/title/tt"]')].find(a => rensa(a.textContent));
        titel = rensa(lank?.textContent || lank?.getAttribute('aria-label'));
      }
      const ar = [...li.querySelectorAll('span, div, li')]
        .filter(el => !el.children.length).map(el => el.textContent.trim())
        .find(t => /^\d{4}(–(\d{4})?)?$/.test(t));
      return titel ? (ar ? `${titel} (${ar})` : titel) : '';
    }).filter(Boolean);
    if (rader.length >= imdb.length / 2) {
      ladda(rader.join('\n') + '\n', 'text/plain', `${namn}.txt`);
      visa(`Klart (${resultat}). ${rader.length} av ${imdb.length} titlar sparade i ${namn}.txt.`);
      return;
    }
    // Hittades inte titlarna har IMDb ändrat sidan: spara den som HTML så att det går att rätta
    visa(`Hittade bara ${rader.length} titlar i ${imdb.length} poster. Sparar sidan som HTML i stället.`);
    await sov(1500);
  }

  // Alla andra sidor: spara hela sidan, som listskapare.py sedan läser
  ruta.remove();
  const html = '<!doctype html>\n' + document.documentElement.outerHTML;
  document.body.appendChild(ruta);
  ladda(html, 'text/html', `${namn}.html`);
  visa(`Klart (${resultat}). Sidan sparad som ${namn}.html.`);
})();
