async function loadBusinesses(){
  const res = await fetch('businesses.json');
  const data = await res.json();
  return data;
}

function renderList(businesses){
  const container = document.getElementById('results');
  container.innerHTML = '';
  if(!businesses.length){
    container.innerHTML = '<p>No results found.</p>';
    return;
  }
  businesses.forEach(b => {
    const el = document.createElement('article');
    el.className = 'card';
    el.innerHTML = `
      <h3>${b.name}</h3>
      <div class="meta">${b.category} — ${b.address}</div>
      <div class="desc">${b.description}</div>
      <div class="actions">
        <a class="btn" href="tel:${b.phone}">Call</a>
        ${b.website?`<a class="btn" href="${b.website}" target="_blank">Website</a>`:''}
      </div>
    `;
    container.appendChild(el);
  });
}

function uniqCategories(list){
  const s = new Set(list.map(b=>b.category));
  return Array.from(s).sort();
}

function setupFilters(businesses){
  const search = document.getElementById('search');
  const cat = document.getElementById('category');

  const cats = uniqCategories(businesses);
  cats.forEach(c => {
    const o = document.createElement('option'); o.value=c; o.textContent=c; cat.appendChild(o);
  });

  function apply(){
    const q = search.value.trim().toLowerCase();
    const cval = cat.value;
    const filtered = businesses.filter(b => {
      const matchesQ = !q || (b.name+b.description+b.address+b.phone).toLowerCase().includes(q);
      const matchesC = !cval || b.category === cval;
      return matchesQ && matchesC;
    });
    renderList(filtered);
  }

  search.addEventListener('input', apply);
  cat.addEventListener('change', apply);
  apply();
}

document.addEventListener('DOMContentLoaded', async ()=>{
  const businesses = await loadBusinesses();
  setupFilters(businesses);
});
