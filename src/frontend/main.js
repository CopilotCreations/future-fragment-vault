/**
 * Time Capsule Web - Main JavaScript
 * Handles capsule creation, display, and interaction
 */

// API Base URL
const API_BASE = '/api';

// Application State
const state = {
    currentView: 'collage',
    capsules: [],
    lockedCapsules: [],
    tags: [],
    selectedContentType: 'text',
    drawingContext: null,
    isDrawing: false
};

// DOM Elements
const elements = {
    navBtns: document.querySelectorAll('.nav-btn'),
    views: document.querySelectorAll('.view'),
    collageContainer: document.getElementById('collage-container'),
    upcomingContainer: document.getElementById('upcoming-container'),
    capsuleForm: document.getElementById('capsule-form'),
    searchInput: document.getElementById('search-input'),
    filterType: document.getElementById('filter-type'),
    filterTag: document.getElementById('filter-tag'),
    modal: document.getElementById('capsule-modal'),
    modalBody: document.getElementById('modal-body'),
    modalClose: document.querySelector('.modal-close'),
    typeBtns: document.querySelectorAll('.type-btn'),
    textContentGroup: document.getElementById('text-content-group'),
    drawingContentGroup: document.getElementById('drawing-content-group'),
    codeContentGroup: document.getElementById('code-content-group'),
    drawingCanvas: document.getElementById('drawing-canvas'),
    brushColor: document.getElementById('brush-color'),
    brushSize: document.getElementById('brush-size'),
    clearCanvas: document.getElementById('clear-canvas'),
    statTotal: document.getElementById('stat-total'),
    statUnlocked: document.getElementById('stat-unlocked'),
    statLocked: document.getElementById('stat-locked')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initForm();
    initDrawingCanvas();
    initFilters();
    initModal();
    loadStats();
    loadCapsules();
    loadLockedCapsules();
    loadTags();
    setMinUnlockDate();
});

// Navigation
function initNavigation() {
    elements.navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            switchView(view);
        });
    });
}

function switchView(view) {
    state.currentView = view;
    
    elements.navBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });
    
    elements.views.forEach(v => {
        v.classList.toggle('active', v.id === `${view}-view`);
    });
}

// Form Handling
function initForm() {
    elements.capsuleForm.addEventListener('submit', handleFormSubmit);
    
    elements.typeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            selectContentType(btn.dataset.type);
        });
    });
}

function selectContentType(type) {
    state.selectedContentType = type;
    
    elements.typeBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === type);
    });
    
    elements.textContentGroup.classList.toggle('hidden', type !== 'text');
    elements.drawingContentGroup.classList.toggle('hidden', type !== 'drawing');
    elements.codeContentGroup.classList.toggle('hidden', type !== 'code');
}

function setMinUnlockDate() {
    const unlockDateInput = document.getElementById('unlock-date');
    const now = new Date();
    now.setMinutes(now.getMinutes() + 5); // Minimum 5 minutes in the future
    unlockDateInput.min = now.toISOString().slice(0, 16);
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    let content = '';
    
    switch (state.selectedContentType) {
        case 'text':
            content = document.getElementById('capsule-content').value;
            break;
        case 'drawing':
            content = elements.drawingCanvas.toDataURL('image/png');
            break;
        case 'code':
            const language = document.getElementById('code-language').value;
            const code = document.getElementById('code-content').value;
            content = JSON.stringify({ language, code });
            break;
    }
    
    if (!content) {
        showToast('Please add some content to your capsule!');
        return;
    }
    
    const capsuleData = {
        title: formData.get('title'),
        content: content,
        content_type: state.selectedContentType,
        creator_name: formData.get('creator_name'),
        unlock_date: new Date(formData.get('unlock_date')).toISOString(),
        tags: formData.get('tags') ? formData.get('tags').split(',').map(t => t.trim()) : [],
        is_public: document.getElementById('is-public').checked
    };
    
    try {
        const response = await fetch(`${API_BASE}/capsules`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(capsuleData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('🚀 Capsule launched into the future!');
            e.target.reset();
            clearDrawingCanvas();
            selectContentType('text');
            loadStats();
            loadLockedCapsules();
            switchView('upcoming');
        } else {
            showToast(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Error creating capsule:', error);
        showToast('Failed to create capsule. Please try again.');
    }
}

// Drawing Canvas
function initDrawingCanvas() {
    if (!elements.drawingCanvas) return;
    
    state.drawingContext = elements.drawingCanvas.getContext('2d');
    clearDrawingCanvas();
    
    elements.drawingCanvas.addEventListener('mousedown', startDrawing);
    elements.drawingCanvas.addEventListener('mousemove', draw);
    elements.drawingCanvas.addEventListener('mouseup', stopDrawing);
    elements.drawingCanvas.addEventListener('mouseout', stopDrawing);
    
    // Touch support
    elements.drawingCanvas.addEventListener('touchstart', handleTouchStart);
    elements.drawingCanvas.addEventListener('touchmove', handleTouchMove);
    elements.drawingCanvas.addEventListener('touchend', stopDrawing);
    
    elements.clearCanvas.addEventListener('click', clearDrawingCanvas);
}

function startDrawing(e) {
    state.isDrawing = true;
    draw(e);
}

function draw(e) {
    if (!state.isDrawing) return;
    
    const rect = elements.drawingCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    state.drawingContext.lineWidth = elements.brushSize.value;
    state.drawingContext.lineCap = 'round';
    state.drawingContext.strokeStyle = elements.brushColor.value;
    
    state.drawingContext.lineTo(x, y);
    state.drawingContext.stroke();
    state.drawingContext.beginPath();
    state.drawingContext.moveTo(x, y);
}

function stopDrawing() {
    state.isDrawing = false;
    state.drawingContext.beginPath();
}

function handleTouchStart(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousedown', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    elements.drawingCanvas.dispatchEvent(mouseEvent);
}

function handleTouchMove(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    elements.drawingCanvas.dispatchEvent(mouseEvent);
}

function clearDrawingCanvas() {
    if (!state.drawingContext) return;
    state.drawingContext.fillStyle = 'white';
    state.drawingContext.fillRect(0, 0, elements.drawingCanvas.width, elements.drawingCanvas.height);
}

// Filters
function initFilters() {
    elements.searchInput.addEventListener('input', debounce(loadCapsules, 300));
    elements.filterType.addEventListener('change', loadCapsules);
    elements.filterTag.addEventListener('change', loadCapsules);
}

// Modal
function initModal() {
    elements.modalClose.addEventListener('click', closeModal);
    elements.modal.addEventListener('click', (e) => {
        if (e.target === elements.modal) closeModal();
    });
}

function openModal(capsule) {
    let contentHtml = '';
    
    if (capsule.content_type === 'drawing') {
        contentHtml = `<img src="${capsule.content}" alt="Drawing" class="modal-drawing">`;
    } else if (capsule.content_type === 'code') {
        try {
            const codeData = JSON.parse(capsule.content);
            contentHtml = `
                <p style="margin-bottom: 10px; color: var(--text-secondary);">Language: ${codeData.language}</p>
                <pre class="modal-content-body code">${escapeHtml(codeData.code)}</pre>
            `;
        } catch {
            contentHtml = `<pre class="modal-content-body code">${escapeHtml(capsule.content)}</pre>`;
        }
    } else {
        contentHtml = `<div class="modal-content-body">${escapeHtml(capsule.content)}</div>`;
    }
    
    elements.modalBody.innerHTML = `
        <h2 class="modal-title">${escapeHtml(capsule.title)}</h2>
        <div class="modal-meta">
            <span>Created by ${escapeHtml(capsule.creator_name)}</span> • 
            <span>Unlocked ${formatDate(capsule.unlock_date)}</span>
        </div>
        ${contentHtml}
        ${capsule.tags && capsule.tags.length ? `
            <div class="fragment-tags" style="margin-top: 20px;">
                ${capsule.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
            </div>
        ` : ''}
    `;
    
    elements.modal.classList.add('active');
}

function closeModal() {
    elements.modal.classList.remove('active');
}

// API Functions
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        
        elements.statTotal.textContent = data.total;
        elements.statUnlocked.textContent = data.unlocked;
        elements.statLocked.textContent = data.locked;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadCapsules() {
    const search = elements.searchInput.value;
    const contentType = elements.filterType.value;
    const tag = elements.filterTag.value;
    
    let url = `${API_BASE}/capsules/unlocked?limit=30`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        let capsules = data.capsules || [];
        
        // Apply client-side filters
        if (search) {
            const searchLower = search.toLowerCase();
            capsules = capsules.filter(c => 
                c.title.toLowerCase().includes(searchLower) ||
                (c.content && c.content.toLowerCase().includes(searchLower))
            );
        }
        
        if (contentType) {
            capsules = capsules.filter(c => c.content_type === contentType);
        }
        
        if (tag) {
            capsules = capsules.filter(c => c.tags && c.tags.includes(tag));
        }
        
        state.capsules = capsules;
        renderCollage(capsules);
    } catch (error) {
        console.error('Error loading capsules:', error);
    }
}

async function loadLockedCapsules() {
    try {
        const response = await fetch(`${API_BASE}/capsules/locked?limit=20`);
        const data = await response.json();
        
        state.lockedCapsules = data.capsules || [];
        renderUpcoming(state.lockedCapsules);
    } catch (error) {
        console.error('Error loading locked capsules:', error);
    }
}

async function loadTags() {
    try {
        const response = await fetch(`${API_BASE}/tags`);
        const data = await response.json();
        
        state.tags = data.tags || [];
        
        elements.filterTag.innerHTML = '<option value="">All Tags</option>';
        state.tags.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag;
            option.textContent = tag;
            elements.filterTag.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading tags:', error);
    }
}

// Render Functions
function renderCollage(capsules) {
    if (!capsules.length) {
        elements.collageContainer.innerHTML = '<p class="empty-message">No unlocked capsules yet. Be the first to create one!</p>';
        return;
    }
    
    elements.collageContainer.innerHTML = '';
    
    capsules.forEach((capsule, index) => {
        const fragment = document.createElement('div');
        fragment.className = `capsule-fragment ${capsule.content_type}-type`;
        fragment.style.left = `${capsule.fragment_x}%`;
        fragment.style.top = `${capsule.fragment_y}%`;
        fragment.style.setProperty('--rotation', `${capsule.fragment_rotation}deg`);
        fragment.style.setProperty('--scale', capsule.fragment_scale);
        fragment.style.transform = `translate(-50%, -50%) rotate(${capsule.fragment_rotation}deg) scale(${capsule.fragment_scale})`;
        fragment.style.animationDelay = `${index * 0.1}s`;
        fragment.style.zIndex = Math.floor(Math.random() * 10);
        
        let preview = '';
        if (capsule.content_type === 'drawing') {
            preview = '🎨 [Drawing]';
        } else if (capsule.content_type === 'code') {
            preview = '💻 [Code Snippet]';
        } else {
            preview = capsule.content ? capsule.content.substring(0, 100) + (capsule.content.length > 100 ? '...' : '') : '';
        }
        
        fragment.innerHTML = `
            <h3 class="fragment-title">${escapeHtml(capsule.title)}</h3>
            <p class="fragment-preview">${escapeHtml(preview)}</p>
            <div class="fragment-meta">
                <span>${escapeHtml(capsule.creator_name)}</span>
                <span>${formatDate(capsule.created_at)}</span>
            </div>
            ${capsule.tags && capsule.tags.length ? `
                <div class="fragment-tags">
                    ${capsule.tags.slice(0, 3).map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
        `;
        
        fragment.addEventListener('click', () => openModal(capsule));
        
        elements.collageContainer.appendChild(fragment);
    });
}

function renderUpcoming(capsules) {
    if (!capsules.length) {
        elements.upcomingContainer.innerHTML = '<p class="empty-message">No capsules waiting to be unlocked.</p>';
        return;
    }
    
    elements.upcomingContainer.innerHTML = '';
    
    capsules.forEach(capsule => {
        const card = document.createElement('div');
        card.className = 'upcoming-capsule';
        
        const timeRemaining = capsule.time_remaining || { days: 0, hours: 0, minutes: 0 };
        
        card.innerHTML = `
            <h3 class="upcoming-title">${escapeHtml(capsule.title)}</h3>
            <p class="upcoming-meta">By ${escapeHtml(capsule.creator_name)}</p>
            <div class="countdown">
                <div class="countdown-item">
                    <span class="countdown-value">${timeRemaining.days}</span>
                    <span class="countdown-label">Days</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-value">${timeRemaining.hours}</span>
                    <span class="countdown-label">Hours</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-value">${timeRemaining.minutes}</span>
                    <span class="countdown-label">Minutes</span>
                </div>
            </div>
            <p class="upcoming-meta" style="margin-top: 15px;">
                🔓 Unlocks: ${formatDate(capsule.unlock_date)}
            </p>
        `;
        
        elements.upcomingContainer.appendChild(card);
    });
}

// Utility Functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
