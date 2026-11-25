// Listskapare för IMDb-listor. Körs i din egen webbläsare, på en öppen IMDb-sida
// med en lista (t.ex. Top 1000-sökningen). Skriptet klickar "50 more" tills alla
// poster har laddats och laddar sedan ner en .txt-fil med en titel per rad.
//
// Användning: öppna sidan, tryck F12 > fliken Console, klistra in hela filen, Enter.
// Eller använd bokmärket i README.md.
(async () => {
  const PAUS = 1500;      // ms mellan klicken, för att inte belasta sidan
  const VANTA_MAX = 20000; // ms att vänta på att nya poster laddas
  const sov = ms => new Promise(r => setTimeout(r, ms));
  const poster = () => document.querySelectorAll('li.ipc-metadata-list-summary-item');
  const knapp = () => [...document.querySelectorAll('button')]
    .find(b => /^\s*\d+\s+more\s*$/i.test(b.textContent) || /^\s*\d+\s+till\s*$/i.test(b.textContent));

  const ruta = document.createElement('div');
  ruta.style.cssText = 'position:fixed;top:12px;right:12px;z-index:99999;background:#06202b;' +
    'color:#f2fbfa;font:15px/1.4 sans-serif;padding:12px 16px;border-radius:8px;' +
    'box-shadow:0 4px 16px rgba(0,0,0,.4)';
  document.body.appendChild(ruta);
  const visa = t => { ruta.textContent = 'Listskapare: ' + t; };

  // 1. Ladda alla poster
  let b;
  while ((b = knapp())) {
    const fore = poster().length;
    visa(`${fore} poster laddade, hämtar fler …`);
    b.scrollIntoView({ block: 'center' });
    b.click();
    const start = Date.now();
    while (poster().length === fore && Date.now() - start < VANTA_MAX) await sov(300);
    if (poster().length === fore) { visa(`Inget nytt laddades efter ${fore} poster. Avbryter laddningen.`); await sov(2000); break; }
    await sov(PAUS);
  }

  // 2. Plocka ut titel och år
  const rader = [...poster()].map(li => {
    const titel = (li.querySelector('h3')?.textContent || '').replace(/^\s*\d+\.\s*/, '').trim();
    const ar = [...li.querySelectorAll('span')].map(s => s.textContent.trim())
      .find(t => /^\d{4}(–(\d{4})?)?$/.test(t));
    return titel ? (ar ? `${titel} (${ar})` : titel) : '';
  }).filter(Boolean);

  // 3. Ladda ner som .txt
  const namn = (document.title || 'imdb-lista').replace(/[^\wåäöÅÄÖ-]+/g, '-').replace(/-+$/, '').toLowerCase();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([rader.join('\n') + '\n'], { type: 'text/plain;charset=utf-8' }));
  a.download = `${namn}.txt`;
  document.body.appendChild(a); a.click(); a.remove();
  visa(`Klart: ${rader.length} titlar sparade i ${namn}.txt`);
})();
