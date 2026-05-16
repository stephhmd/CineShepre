/**
 * CineSphere - Frontend Phase 4
 * Consume la API FastAPI local (películas, favoritos).
 * Vanilla JS, sin frameworks.
 */

const API_URL = 'http://localhost:8000';
const USER_ID = 'alejandro';

// Referencias a elementos del DOM
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

// Película actual mostrada
let currentSearchResult = null;

// --- Utilidades ---

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

function setLoading(buttonElement, loading) {
  if (!buttonElement) return;
  buttonElement.disabled = loading;
  buttonElement.textContent = loading
    ? 'Cargando...'
    : (buttonElement === searchBtn ? 'Buscar' : 'Guardar en favoritos');
}

// --- Búsqueda ---

async function searchMovie() {
  const criterio = (searchInput.value || '').trim();

  if (!criterio) {
    showFeedback('Escribe el nombre de una película para buscar.', 'error');
    return;
  }

  hideFeedback();
  setLoading(searchBtn, true);

  resultSection.classList.add('hidden');
  currentSearchResult = null;

  try {
    const res = await fetch(`${API_URL}/pelicula/${encodeURIComponent(criterio)}`);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      showFeedback(data.detail || `Error ${res.status}`, 'error');
      return;
    }

    currentSearchResult = data;
    renderResultCard(data);
    resultSection.classList.remove('hidden');
    notesInput.value = '';

  } catch (err) {
    showFeedback('No se pudo conectar con el servidor. ¿Está corriendo la API en el puerto 8000?', 'error');
  } finally {
    setLoading(searchBtn, false);
  }
}

function renderResultCard(movie) {
  const img = movie.image
    ? `<img src="${movie.image}" class="w-full h-64 object-cover" />`
    : `<div class="w-full h-64 bg-gray-700 flex items-center justify-center text-gray-500">Sin imagen</div>`;

  const rating = movie.rating != null ? movie.rating.toFixed(1) : '-';
  const date = movie.release_date || '-';

  resultCard.innerHTML = `
    ${img}
    <div class="p-4">
      <h3 class="font-semibold text-lg">${escapeHtml(movie.title)}</h3>
      <div class="flex gap-3 mt-2 text-sm text-gray-400">
        <span>⭐ ${rating}</span>
        <span>📅 ${date}</span>
        <span>${escapeHtml(movie.media_type || 'movie')}</span>
      </div>
    </div>
  `;
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// --- Guardar favorito ---

async function saveFavorite() {
  if (!currentSearchResult) {
    showFeedback('Primero busca una película.', 'error');
    return;
  }

  const payload = {
    external_id: currentSearchResult.id,
    title: currentSearchResult.title,
    media_type: currentSearchResult.media_type || 'movie',
    rating: currentSearchResult.rating ?? null,
    release_date: currentSearchResult.release_date || null,
    image: currentSearchResult.image || null,
    notas_personales: (notesInput.value || '').trim() || null
  };

  setLoading(saveFavoriteBtn, true);
  hideFeedback();

  try {
    const res = await fetch(`${API_URL}/recursos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': USER_ID
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json().catch(() => ({}));

    if (res.status === 201) {
      showFeedback('Película guardada en favoritos.', 'success');
      loadFavorites();
    } else if (res.status === 409) {
      showFeedback(data.detail || 'Ya existe en favoritos.', 'error');
    } else {
      showFeedback(data.detail || `Error ${res.status}`, 'error');
    }

  } catch (err) {
    showFeedback('Error de conexión al guardar.', 'error');
  } finally {
    setLoading(saveFavoriteBtn, false);
  }
}

// --- Favoritos ---

async function loadFavorites() {
  favoritesEmpty.textContent = 'Cargando favoritos...';
  favoritesEmpty.classList.remove('hidden');
  favoritesList.querySelectorAll('.favorite-card').forEach(el => el.remove());

  try {
    const res = await fetch(`${API_URL}/recursos`, {
      headers: { 'X-User-Id': USER_ID }
    });

    const data = await res.json().catch(() => []);

    if (!res.ok) {
      favoritesEmpty.textContent = 'Error al cargar favoritos.';
      return;
    }

    const items = Array.isArray(data) ? data : [];

    if (items.length === 0) {
      favoritesEmpty.textContent = 'Aún no tienes favoritos.';
      return;
    }

    favoritesEmpty.classList.add('hidden');

    items.forEach(item => {
      const card = document.createElement('div');
      card.className = 'favorite-card bg-gray-800 rounded-xl p-4 flex gap-4';

      card.innerHTML = `
        <div class="flex-1">
          <h3 class="font-semibold">${escapeHtml(item.title)}</h3>
          <p class="text-sm text-gray-400">⭐ ${item.rating ?? '-'} · ${item.release_date ?? '-'}</p>
        </div>
      `;

      favoritesList.appendChild(card);
    });

  } catch (err) {
    favoritesEmpty.textContent = 'No se pudo conectar con el servidor.';
  }
}

// --- Eventos ---

searchBtn.addEventListener('click', searchMovie);
searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') searchMovie();
});

saveFavoriteBtn.addEventListener('click', saveFavorite);
refreshFavoritesBtn.addEventListener('click', loadFavorites);

// Init
loadFavorites();



function showLogin() {
  document.getElementById("authViewContainer").classList.remove("hidden");
  document.getElementById("authTitle").innerText = "Iniciar sesión";
  document.getElementById("authSubmit").innerText = "Entrar";
}

function showRegister() {
  document.getElementById("authViewContainer").classList.remove("hidden");
  document.getElementById("authTitle").innerText = "Registrarse";
  document.getElementById("authSubmit").innerText = "Crear cuenta";
}

function login() {
  const user = document.getElementById("authUser").value;
  const pass = document.getElementById("authPass").value;

  if (!user || !pass) return;

  localStorage.setItem("user", user);

  setLoggedIn();
}

function logout() {
  localStorage.removeItem("user");
  setLoggedOut();
}

function setLoggedIn() {
  document.getElementById("authButtons").classList.add("hidden");
  document.getElementById("logoutBtn").classList.remove("hidden");
  document.getElementById("authViewContainer").classList.add("hidden");
}

function setLoggedOut() {
  document.getElementById("authButtons").classList.remove("hidden");
  document.getElementById("logoutBtn").classList.add("hidden");
}

window.onload = () => {
  if (localStorage.getItem("user")) {
    setLoggedIn();
  } else {
    setLoggedOut();
  }
};