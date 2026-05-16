/**
 * CineSphere - Frontend Phase 4
 */

const API_URL =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000"
    : "https://TU-BACKEND.onrender.com";

// 🔥 Usuario dinámico
function getUserId() {
  return localStorage.getItem("user") || "anon";
}

// Referencias DOM
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const feedback = document.getElementById('feedback');
const resultSection = document.getElementById('resultSection');
const resultCard = document.getElementById('resultCard');
const notesInput = document.getElementById('notesInput');
const saveFavoriteBtn = document.getElementById('saveFavoriteBtn');
const favoritesList = document.getElementById('favoritesList');
const favoritesEmpty = document.getElementById('favoritesEmpty');
const refreshFavoritesBtn = document.getElementById('refreshFavoritesBtn');

let currentSearchResult = null;

// --- UI helpers ---

function showFeedback(message, type = 'info') {
  feedback.classList.remove('hidden');
  feedback.className = 'mb-6 p-4 rounded-xl ';

  if (type === 'error') {
    feedback.className += 'bg-red-900/50 border border-red-600 text-red-200';
  } else if (type === 'success') {
    feedback.className += 'bg-emerald-900/50 border border-emerald-600 text-emerald-200';
  } else {
    feedback.className += 'bg-gray-700 text-gray-200';
  }

  feedback.textContent = message;
}

function hideFeedback() {
  feedback.classList.add('hidden');
}

function setLoading(button, loading) {
  if (!button) return;
  button.disabled = loading;
  button.textContent = loading
    ? 'Cargando...'
    : (button === searchBtn ? 'Buscar' : 'Guardar favorito');
}

// --- SEARCH ---

async function searchMovie() {
  const criterio = searchInput.value.trim();

  if (!criterio) {
    showFeedback('Escribe una película.', 'error');
    return;
  }

  hideFeedback();
  setLoading(searchBtn, true);
  resultSection.classList.add('hidden');

  try {
    const res = await fetch(`${API_URL}/pelicula/${encodeURIComponent(criterio)}`);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      showFeedback(data.detail || 'Error buscando película', 'error');
      return;
    }

    currentSearchResult = data;
    renderResultCard(data);
    resultSection.classList.remove('hidden');
    notesInput.value = '';

  } catch {
    showFeedback('No conecta con el backend 😵', 'error');
  } finally {
    setLoading(searchBtn, false);
  }
}

function renderResultCard(movie) {
  const img = movie.image
    ? `<img src="${movie.image}" class="w-full h-64 object-cover" />`
    : `<div class="w-full h-64 bg-gray-700 flex items-center justify-center">Sin imagen</div>`;

  resultCard.innerHTML = `
    ${img}
    <div class="p-4">
      <h3 class="text-lg font-semibold">${escapeHtml(movie.title)}</h3>
      <p class="text-sm text-gray-400 mt-2">
        ⭐ ${movie.rating ?? '-'} · 📅 ${movie.release_date ?? '-'}
      </p>
    </div>
  `;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// --- SAVE FAVORITE ---

async function saveFavorite() {

  if (!getUserId() || getUserId() === "anon") {
    showFeedback("Inicia sesión primero.", "error");
    return;
  }

  if (!currentSearchResult) {
    showFeedback('Busca una película primero.', 'error');
    return;
  }

  const payload = {
    external_id: currentSearchResult.id,
    title: currentSearchResult.title,
    media_type: currentSearchResult.media_type || 'movie',
    rating: currentSearchResult.rating ?? null,
    release_date: currentSearchResult.release_date || null,
    image: currentSearchResult.image || null,
    notas_personales: notesInput.value.trim() || null
  };

  setLoading(saveFavoriteBtn, true);

  try {
    const res = await fetch(`${API_URL}/recursos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': getUserId()
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json().catch(() => ({}));

    if (res.status === 201) {
      showFeedback('Guardado en favoritos 🎉', 'success');
      loadFavorites();
    } else if (res.status === 409) {
      showFeedback('Ya existe en favoritos.', 'error');
    } else {
      showFeedback(data.detail || 'Error guardando', 'error');
    }

  } catch {
    showFeedback('Error de conexión', 'error');
  } finally {
    setLoading(saveFavoriteBtn, false);
  }
}

// --- FAVORITES ---

async function loadFavorites() {
  favoritesEmpty.textContent = 'Cargando...';
  favoritesEmpty.classList.remove('hidden');
  favoritesList.innerHTML = '';

  try {
    const res = await fetch(`${API_URL}/recursos`, {
      headers: { 'X-User-Id': getUserId() }
    });

    const data = await res.json().catch(() => []);

    if (!res.ok) {
      favoritesEmpty.textContent = 'Error al cargar';
      return;
    }

    if (!data.length) {
      favoritesEmpty.textContent = 'Sin favoritos aún';
      return;
    }

    favoritesEmpty.classList.add('hidden');

    data.forEach(item => {
      const div = document.createElement('div');
      div.className = 'bg-gray-800 p-4 rounded-xl mb-3';

      div.innerHTML = `
        <h3 class="font-semibold">${escapeHtml(item.title)}</h3>
        <p class="text-sm text-gray-400">
          ⭐ ${item.rating ?? '-'} · ${item.release_date ?? '-'}
        </p>
      `;

      favoritesList.appendChild(div);
    });

  } catch {
    favoritesEmpty.textContent = 'No conecta con backend';
  }
}

// --- EVENTS ---

searchBtn.addEventListener('click', searchMovie);

searchInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') searchMovie();
});

saveFavoriteBtn.addEventListener('click', saveFavorite);
refreshFavoritesBtn.addEventListener('click', loadFavorites);

// --- AUTH UI ---

function showLogin(){
  document.getElementById("authModal").classList.remove("hidden");
}

function showRegister(){
  document.getElementById("authModal").classList.remove("hidden");
}

function closeAuth(){
  document.getElementById("authModal").classList.add("hidden");
}

function submitAuth(){
  const user = document.getElementById("username").value;

  if(!user){
    alert("Escribe un usuario");
    return;
  }

  localStorage.setItem("user", user);

  document.getElementById("authButtons").classList.add("hidden");
  document.getElementById("userPanel").classList.remove("hidden");
  document.getElementById("userText").innerText = "Hola, " + user;

  closeAuth();
}

function logout(){
  localStorage.removeItem("user");

  document.getElementById("authButtons").classList.remove("hidden");
  document.getElementById("userPanel").classList.add("hidden");
}

// INIT
window.onload = () => {
  const user = localStorage.getItem("user");

  if(user){
    document.getElementById("authButtons").classList.add("hidden");
    document.getElementById("userPanel").classList.remove("hidden");
    document.getElementById("userText").innerText = "Hola, " + user;
  }

  loadFavorites();
};