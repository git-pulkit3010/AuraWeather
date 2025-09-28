// Modern Weather Dashboard JavaScript with Theme Toggle
// Connects to FastAPI backend

class WeatherDashboard {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.cache = new Map();
        this.cacheDuration = 5 * 60 * 1000; // 5 minutes

        this.initializeTheme();
        this.initializeEventListeners();
        this.initializeTabs();
        this.initializeThemeToggle();
    }

    initializeTheme() {
        // Set dark mode as default on first load
        if (!localStorage.getItem('theme')) {
            localStorage.setItem('theme', 'dark');
            document.documentElement.classList.add('dark');
        } else {
            const theme = localStorage.getItem('theme');
            if (theme === 'dark') {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        }
        this.updateThemeIndicator();
    }

    initializeThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        themeToggle.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Add keyboard support for theme toggle
        themeToggle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }

    toggleTheme() {
        const html = document.documentElement;
        const isDark = html.classList.contains('dark');

        if (isDark) {
            html.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }

        this.updateThemeIndicator();

        // Add a subtle animation feedback
        const toggle = document.getElementById('theme-toggle');
        toggle.style.transform = 'scale(0.95)';
        setTimeout(() => {
            toggle.style.transform = 'scale(1)';
        }, 150);
    }

    updateThemeIndicator() {
        const indicator = document.getElementById('theme-indicator');
        const isDark = document.documentElement.classList.contains('dark');
        indicator.textContent = isDark ? 'Dark Mode' : 'Light Mode';
    }

    initializeEventListeners() {
        // Form submissions
        document.getElementById('alerts-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAlertsForm();
        });

        document.getElementById('city-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCityForm();
        });

        document.getElementById('coordinates-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCoordinatesForm();
        });

        // Input validation
        document.getElementById('state-input').addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase().replace(/[^A-Z]/g, '');
        });

        // Add enhanced focus states for better accessibility
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('focus', (e) => {
                e.target.parentElement.classList.add('ring-2', 'ring-blue-400');
            });
            input.addEventListener('blur', (e) => {
                e.target.parentElement.classList.remove('ring-2', 'ring-blue-400');
            });
        });
    }

    initializeTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabPanes = document.querySelectorAll('.tab-pane');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.dataset.tab;
                this.switchTab(targetTab, tabButtons, tabPanes);
            });

            // Keyboard navigation for tabs
            button.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                    e.preventDefault();
                    const buttons = Array.from(tabButtons);
                    const currentIndex = buttons.indexOf(button);
                    let nextIndex;

                    if (e.key === 'ArrowRight') {
                        nextIndex = (currentIndex + 1) % buttons.length;
                    } else {
                        nextIndex = (currentIndex - 1 + buttons.length) % buttons.length;
                    }

                    buttons[nextIndex].focus();
                    buttons[nextIndex].click();
                }
            });
        });
    }

    switchTab(targetTab, tabButtons, tabPanes) {
        // Update button states with comprehensive dark mode support
        tabButtons.forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-selected', 'false');
        });

        const activeButton = document.querySelector(`[data-tab="${targetTab}"]`);
        activeButton.classList.add('active');
        activeButton.setAttribute('aria-selected', 'true');

        // Update tab panes
        tabPanes.forEach(pane => {
            pane.classList.add('hidden');
            pane.classList.remove('active');
        });

        const targetPane = document.getElementById(`${targetTab}-tab`);
        if (targetPane) {
            targetPane.classList.remove('hidden');
            targetPane.classList.add('active');
        }

        // Clear results when switching tabs
        this.clearResults();
    }

    async handleAlertsForm() {
        const stateInput = document.getElementById('state-input');
        const state = stateInput.value.trim().toUpperCase();

        if (!state || state.length !== 2) {
            this.showError('Please enter a valid 2-letter US state code');
            return;
        }

        const button = document.querySelector('#alerts-form button');
        this.setLoadingState(button, true);
        this.clearResults();

        try {
            const response = await fetch(`${this.baseURL}/api/alerts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ state })
            });

            const result = await response.json();

            if (result.success && result.data) {
                this.displayAlerts(result.data, result.cached);
            } else {
                this.showError(result.error || 'Failed to fetch weather alerts');
            }
        } catch (error) {
            this.showError(`Connection error: ${error.message}`);
        } finally {
            this.setLoadingState(button, false);
        }
    }

    async handleCityForm() {
        const cityInput = document.getElementById('city-input');
        const city = cityInput.value.trim();

        if (!city) {
            this.showError('Please enter a city name');
            return;
        }

        const button = document.querySelector('#city-form button');
        this.setLoadingState(button, true);
        this.clearResults();

        try {
            const response = await fetch(`${this.baseURL}/api/forecast/city`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ city })
            });

            const result = await response.json();

            if (result.success && result.data) {
                this.displayForecast(result.data, result.cached);
            } else {
                this.showError(result.error || 'Failed to fetch city forecast');
            }
        } catch (error) {
            this.showError(`Connection error: ${error.message}`);
        } finally {
            this.setLoadingState(button, false);
        }
    }

    async handleCoordinatesForm() {
        const latInput = document.getElementById('latitude-input');
        const lonInput = document.getElementById('longitude-input');

        const latitude = parseFloat(latInput.value);
        const longitude = parseFloat(lonInput.value);

        if (isNaN(latitude) || isNaN(longitude)) {
            this.showError('Please enter valid numeric coordinates');
            return;
        }

        if (latitude < -90 || latitude > 90) {
            this.showError('Latitude must be between -90 and 90');
            return;
        }

        if (longitude < -180 || longitude > 180) {
            this.showError('Longitude must be between -180 and 180');
            return;
        }

        const button = document.querySelector('#coordinates-form button');
        this.setLoadingState(button, true);
        this.clearResults();

        try {
            const response = await fetch(`${this.baseURL}/api/forecast`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ latitude, longitude })
            });

            const result = await response.json();

            if (result.success && result.data) {
                this.displayForecast(result.data, result.cached);
            } else {
                this.showError(result.error || 'Failed to fetch coordinate forecast');
            }
        } catch (error) {
            this.showError(`Connection error: ${error.message}`);
        } finally {
            this.setLoadingState(button, false);
        }
    }

    setLoadingState(button, loading) {
        const buttonText = button.querySelector('.button-text');
        const spinner = button.querySelector('.loading-spinner');

        if (loading) {
            button.disabled = true;
            buttonText.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            button.disabled = false;
            buttonText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    }

    displayAlerts(data, cached = false) {
        const container = document.getElementById('results-container');

        if (!data.alerts || data.alerts.length === 0) {
            container.innerHTML = `
                <div class="glass rounded-xl p-6 animate-slide-up shadow-xl">
                    <div class="text-center">
                        <div class="text-6xl mb-4 animate-pulse-slow">🌤️</div>
                        <h3 class="text-2xl font-bold text-white mb-2">Good News!</h3>
                        <p class="text-white/80">No active weather alerts for ${data.state}</p>
                        ${cached ? '<p class="text-white/60 text-sm mt-2 flex items-center justify-center gap-2"><span class="animate-pulse">⚡</span> Cached result</p>' : ''}
                    </div>
                </div>
            `;
            return;
        }

        const alertsHTML = data.alerts.map((alert, index) => `
            <div class="bg-gradient-to-r from-red-500/30 to-orange-500/30 dark:from-red-600/40 dark:to-orange-600/40 backdrop-blur-sm rounded-xl border border-red-300/30 dark:border-red-400/30 p-6 animate-slide-up shadow-xl" style="animation-delay: ${index * 0.1}s">
                <div class="flex items-start gap-4">
                    <div class="text-3xl animate-pulse-slow">${this.getAlertEmoji(alert.Severity)}</div>
                    <div class="flex-1">
                        <div class="flex flex-wrap items-center gap-2 mb-2">
                            <h4 class="text-xl font-bold text-white">${alert.Event || 'Weather Alert'}</h4>
                            <span class="px-3 py-1 text-xs font-semibold rounded-full ${this.getSeverityClass(alert.Severity)} shadow-md">
                                ${alert.Severity || 'Unknown'}
                            </span>
                        </div>
                        <p class="text-white/90 mb-2"><strong>📍 Area:</strong> ${alert.Area || 'Unknown'}</p>
                        <p class="text-white/80 mb-3">${alert.Description || 'No description available'}</p>
                        <div class="bg-white/10 dark:bg-black/20 backdrop-blur-sm rounded-lg p-3 border border-white/20 dark:border-white/10 shadow-inner">
                            <p class="text-white/90 text-sm"><strong>💡 Instructions:</strong> ${alert.Instructions || 'No specific instructions provided'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="space-y-4">
                <div class="glass rounded-xl p-6 shadow-xl">
                    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
                        <h3 class="text-2xl font-bold text-white">⚠️ Active Weather Alerts for ${data.state}</h3>
                        <span class="px-3 py-1 bg-red-500 dark:bg-red-600 text-white text-sm font-semibold rounded-full shadow-md animate-pulse-slow">
                            ${data.count} Alert${data.count !== 1 ? 's' : ''}
                        </span>
                    </div>
                    ${cached ? '<p class="text-white/60 text-sm mb-4 flex items-center gap-2"><span class="animate-pulse">⚡</span> Showing cached results</p>' : ''}
                </div>
                ${alertsHTML}
            </div>
        `;
    }

    displayForecast(data, cached = false) {
        const container = document.getElementById('results-container');

        if (!data.forecast || data.forecast.length === 0) {
            container.innerHTML = `
                <div class="glass rounded-xl p-6 animate-slide-up shadow-xl">
                    <div class="text-center">
                        <div class="text-6xl mb-4">❌</div>
                        <h3 class="text-2xl font-bold text-white mb-2">Forecast Unavailable</h3>
                        <p class="text-white/80">Unable to fetch forecast data for this location</p>
                    </div>
                </div>
            `;
            return;
        }

        const forecastHTML = data.forecast.map((period, index) => `
            <div class="bg-gradient-to-r from-blue-500/30 to-purple-500/30 dark:from-blue-600/40 dark:to-purple-600/40 backdrop-blur-sm rounded-xl border border-blue-300/30 dark:border-blue-400/30 p-6 animate-slide-up shadow-xl" style="animation-delay: ${index * 0.1}s">
                <div class="flex items-start gap-4">
                    <div class="text-4xl animate-pulse-slow">${period.emoji || '🌤️'}</div>
                    <div class="flex-1">
                        <h4 class="text-xl font-bold text-white mb-3">${period.name || 'Unknown Period'}</h4>
                        <div class="grid md:grid-cols-2 gap-4 mb-3">
                            <p class="text-white/90 flex items-center gap-2">
                                <span class="text-lg">🌡️</span>
                                <strong>Temperature:</strong> ${period.Temperature || 'N/A'}
                            </p>
                            <p class="text-white/90 flex items-center gap-2">
                                <span class="text-lg">💨</span>
                                <strong>Wind:</strong> ${period.Wind || 'N/A'}
                            </p>
                        </div>
                        <div class="bg-white/10 dark:bg-black/20 backdrop-blur-sm rounded-lg p-3 border border-white/20 dark:border-white/10 shadow-inner">
                            <p class="text-white/80 text-sm">${period.Forecast || 'No details available'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="space-y-4">
                <div class="glass rounded-xl p-6 shadow-xl">
                    <div class="mb-4">
                        <h3 class="text-2xl font-bold text-white mb-2">🌤️ Weather Forecast</h3>
                        <p class="text-white/80 flex items-center gap-2">
                            <span class="text-lg">📍</span>
                            ${data.location || 'Unknown Location'}
                        </p>
                        ${cached ? '<p class="text-white/60 text-sm mt-2 flex items-center gap-2"><span class="animate-pulse">⚡</span> Showing cached results</p>' : ''}
                    </div>
                </div>
                ${forecastHTML}
            </div>
        `;
    }

    showError(message) {
        const container = document.getElementById('results-container');
        container.innerHTML = `
            <div class="bg-gradient-to-r from-red-500/30 to-red-600/30 dark:from-red-600/40 dark:to-red-700/40 backdrop-blur-sm rounded-xl border border-red-300/30 dark:border-red-400/30 p-6 animate-slide-up shadow-xl">
                <div class="flex items-center gap-4">
                    <div class="text-3xl animate-pulse">❌</div>
                    <div>
                        <h3 class="text-xl font-bold text-white mb-2">Error</h3>
                        <p class="text-white/80">${message}</p>
                    </div>
                </div>
            </div>
        `;
    }

    clearResults() {
        const container = document.getElementById('results-container');
        container.innerHTML = '';
    }

    getAlertEmoji(severity) {
        const severityMap = {
            'extreme': '🔴',
            'high': '🟠',
            'moderate': '🟡',
            'minor': '🟢',
        };
        return severityMap[severity?.toLowerCase()] || '⚠️';
    }

    getSeverityClass(severity) {
        const classMap = {
            'extreme': 'bg-red-600 dark:bg-red-700 text-white',
            'high': 'bg-orange-600 dark:bg-orange-700 text-white',
            'moderate': 'bg-yellow-600 dark:bg-yellow-600 text-white',
            'minor': 'bg-green-600 dark:bg-green-700 text-white',
        };
        return classMap[severity?.toLowerCase()] || 'bg-gray-600 dark:bg-gray-700 text-white';
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WeatherDashboard();
});

// Enhanced console styling with theme awareness
console.log('%c🌤️ Weather Dashboard Loaded!', 'color: #3b82f6; font-size: 18px; font-weight: bold;');
console.log('%c🌙 Dark Mode Active', 'color: #6366f1; font-size: 14px;');
console.log('%cBuilt with modern web technologies', 'color: #6b7280; font-size: 12px;');
