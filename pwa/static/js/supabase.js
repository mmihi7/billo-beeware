// Initialize Supabase client with environment variables
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://fqjvwnbrhfctknlrpyba.supabase.co';
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZxanZ3bmJyaGZjdGtubHJweWJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYyMTYzMzgsImV4cCI6MjA3MTc5MjMzOH0.MEJwtBrmzGpv0JobWoA2W0RaunyiQ50gYmkP8oSaC1g';

// Initialize the Supabase client
export const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true,
        flowType: 'pkce',
        debug: process.env.NODE_ENV === 'development'
    },
    global: {
        headers: {
            'X-Client-Info': 'billo-pwa/1.0.0'
        }
    }
});

// Auth functions
export const signUp = async (email, password, userData) => {
    const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
            data: {
                full_name: userData.fullName,
                role: userData.role,
                restaurant_id: userData.restaurantId
            }
        }
    });
    return { data, error };
};

export const signIn = async (email, password) => {
    return await supabase.auth.signInWithPassword({
        email,
        password
    });
};

export const signOut = async () => {
    return await supabase.auth.signOut();
};

// Get current user
export const getCurrentUser = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
};

// Get user profile
export const getUserProfile = async (userId) => {
    const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single();
    return { data, error };
};

// Subscribe to auth state changes
export const onAuthStateChange = (callback) => {
    return supabase.auth.onAuthStateChange((event, session) => {
        callback(event, session);
    });
};

// Example function to fetch tabs for the current user
export const getUserTabs = async (userId) => {
    const { data, error } = await supabase
        .from('tabs')
        .select('*')
        .eq('opened_by', userId)
        .order('created_at', { ascending: false });
    return { data, error };
};

// Example function to fetch menu items
export const getMenuItems = async (restaurantId) => {
    const { data, error } = await supabase
        .from('menu_items')
        .select('*')
        .eq('restaurant_id', restaurantId)
        .eq('is_available', true);
    return { data, error };
};

export default supabase;
