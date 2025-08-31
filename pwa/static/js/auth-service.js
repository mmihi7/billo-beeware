import { supabase } from './supabase.js';

export class AuthService {
    // Cache for user profile to reduce database calls
    static _userProfile = null;
    static _profilePromise = null;
    // Check if user is authenticated
    static async isAuthenticated() {
        try {
            const { data: { session }, error } = await supabase.auth.getSession();
            if (error) throw error;
            return !!session;
        } catch (error) {
            console.error('Error checking authentication:', error);
            return false;
        }
    }

    // Get current user
    static async getCurrentUser() {
        try {
            const { data: { user }, error } = await supabase.auth.getUser();
            if (error) throw error;
            return user;
        } catch (error) {
            console.error('Error getting current user:', error);
            return null;
        }
    }
    
    // Get user profile with role information
    static async getUserProfile(userId = null) {
        try {
            // Return cached profile if available
            if (this._userProfile) return this._userProfile;
            
            // If a profile fetch is already in progress, return that promise
            if (this._profilePromise) return this._profilePromise;
            
            // Get the user ID if not provided
            if (!userId) {
                const user = await this.getCurrentUser();
                if (!user) return null;
                userId = user.id;
            }
            
            // Fetch profile from the database
            this._profilePromise = (async () => {
                const { data, error } = await supabase
                    .from('profiles')
                    .select('*')
                    .eq('id', userId)
                    .single();
                
                if (error) throw error;
                
                // Cache the profile
                this._userProfile = data;
                return data;
            })();
            
            return await this._profilePromise;
            
        } catch (error) {
            console.error('Error fetching user profile:', error);
            this._profilePromise = null; // Reset promise on error
            return null;
        }
    }

    // Sign in with email and password
    static async signIn(email, password) {
        try {
            const { data, error } = await supabase.auth.signInWithPassword({
                email: email.toLowerCase().trim(),
                password,
            });
            
            if (error) {
                // Handle specific error cases
                if (error.message.includes('Invalid login credentials')) {
                    throw new Error('Invalid email or password. Please try again.');
                }
                throw error;
            }
            
            // Clear cached profile on new sign in
            this._userProfile = null;
            this._profilePromise = null;
            
            return data;
        } catch (error) {
            console.error('Sign in error:', error);
            throw error;
        }
    }

    // Sign up new user
    static async signUp(email, password, userData) {
        try {
            const { data, error } = await supabase.auth.signUp({
                email: email.toLowerCase().trim(),
                password,
                options: {
                    data: {
                        full_name: userData.fullName,
                        role: userData.role,
                        restaurant_id: userData.restaurantId
                    },
                    emailRedirectTo: window.location.origin + '/auth/callback'
                }
            });
            
            if (error) {
                if (error.message.includes('already registered')) {
                    throw new Error('This email is already registered. Please sign in instead.');
                }
                throw error;
            }
            
            return data;
        } catch (error) {
            console.error('Sign up error:', error);
            throw error;
        }
    }

    // Sign out
    static async signOut() {
        try {
            // Clear cached profile
            this._userProfile = null;
            this._profilePromise = null;
            
            // Sign out from Supabase
            const { error } = await supabase.auth.signOut();
            if (error) throw error;
            
            // Clear any stored tokens or session data
            window.localStorage.removeItem('sb-auth-token');
            
        } catch (error) {
            console.error('Sign out error:', error);
            throw error;
        }
    }

    // Handle password reset
    static async resetPassword(email) {
        try {
            const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
                redirectTo: window.location.origin + '/reset-password'
            });
            
            if (error) {
                if (error.message.includes('user not found')) {
                    throw new Error('No account found with this email address.');
                }
                throw error;
            }
            
            return data;
        } catch (error) {
            console.error('Password reset error:', error);
            throw error;
        }
    }
    
    // Update user profile
    static async updateProfile(updates) {
        try {
            const user = await this.getCurrentUser();
            if (!user) throw new Error('Not authenticated');
            
            const { data, error } = await supabase
                .from('profiles')
                .update(updates)
                .eq('id', user.id)
                .select()
                .single();
                
            if (error) throw error;
            
            // Update cached profile
            if (this._userProfile) {
                this._userProfile = { ...this._userProfile, ...updates };
            }
            
            return data;
        } catch (error) {
            console.error('Update profile error:', error);
            throw error;
        }
    }

    // Subscribe to auth state changes
    static onAuthStateChange(callback) {
        return supabase.auth.onAuthStateChange((event, session) => {
            callback(event, session);
        });
    }
}

// Initialize auth state listener
export function initAuthStateListener() {
    AuthService.onAuthStateChange((event, session) => {
        const authEvent = new CustomEvent('auth-state-change', {
            detail: { event, session }
        });
        window.dispatchEvent(authEvent);
    });
}

// Initialize auth state listener when the module loads
initAuthStateListener();
