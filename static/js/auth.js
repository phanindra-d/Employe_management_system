export default class Auth {
    static getAccessToken() {
        return localStorage.getItem('access_token');
    }

    static getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }

    static async refreshToken() {
        try {
            const refresh_token = this.getRefreshToken();
            if (!refresh_token) {
                throw new Error('No refresh token');
            }

            const response = await fetch('/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh_token })
            });

            const data = await response.json();
            if (response.ok) {
                localStorage.setItem('access_token', data.access_token);
                return data.access_token;
            } else {
                throw new Error('Token refresh failed');
            }
        } catch (error) {
            // Clear tokens and redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        }
    }

    static async fetchWithToken(url, options = {}) {
        // Add token to headers
        const token = this.getAccessToken();
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };

        let response = await fetch(url, options);

        // If token expired, try refresh
        if (response.status === 401) {
            const newToken = await this.refreshToken();
            if (newToken) {
                options.headers['Authorization'] = `Bearer ${newToken}`;
                response = await fetch(url, options);
            }
        }

        return response;
    }

    static logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
    }
}